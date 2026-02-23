# %%
# This script reads a csv file representing a PCIe trace and analyzes the relationships of the DATA fields 
# The script presents charts, plots, and/or tables summarizing the patterns in the DATA field
#
# Below is a sample of the input CSV file:
# Marker,Packet,Link Dir,Ord.Set Type,DLLP Type,TLP Type,Link Event,PSN,AckNak_Seq_Num,VC ID,HdrScale,HdrFC,DataScale,DataFC,Feature Ack,Feature Support,TC,LN,TH,NW,TD,EP,Attributes,AT,Length,RequesterID,Tag,CompleterID,Address,DeviceID,Register,1st BE,Last BE,Cpl Status,Byte Cnt,BCM,Lwr Addr,Msg Routing,Message Code,TS Link,TS Lane,N_FTS,Training Control,TS Data Rate,TS Gen3 Eq Control,TS Gen3 Pre-Cursor,TS Gen3 Cursor,TS Gen3 Post-Cursor,PMUX Channel ID,PMUX Metadata,Snoop,Requirement (Snoop),Scale (Snoop),Value (Snoop),No-Snoop,Requirement (No-Snoop),Scale (No-Snoop),Value (No-Snoop),PTM Master Time[63:32],PTM Master Time[31:0],PTM Propagation Delay,ARP Command,Slave Address,Target Address,Device Slave Address,Assign Address,Read,Write,Byte Count,Address Type,PEC Support,UDID Version,Silicon Revision ID,Vendor ID,Device ID,ZONE,IPMI,ASF,OEM,SMBus Version,Sub Vendor ID,Sub Device ID,Vendor Specific ID,PEC,LCRC,ECRC,CRC 16,DATA,Time Delta,Time Stamp,Jammer Phase,Action,Jammer Target Packet,Jammer Result Packet,CXL Pkt Type,CXL Pkt Subtype,OpCode,CQID,UQID,Address [51:6],NT,RSP_PRE,MESI,ChunkValid,Bogus,Poison,Go-Err,MetaField,MetaValue,SnpType,LLCTRL Pkt Subtype,ALMP VLSM State,ALMP VLSM Target
# Marker,0,Upstream,,,MWr(64),,1980,,,,,,,,,,,,,,,,,32,184:00:0,0,,00001F00:0000EE80,,,1111,1111,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0xA33879DB,,,47517350 2A212E71 4F4E6C14 3DF31929 C248B5F8 94220964 99D52B4B F5478502 C8EB0DE5 B239EC56 BF3A98EA 58273A54 30C9F40A F99B82E9 673641E5 81433BB2 24DA2A93 73FCA9C5 60CDDBBE BB758229 01E29181 C901E207 A446BBBC F33E9A59 F16BCED6 0983B86D 4521EAC6 A4C49ADA C3B1CEC3 38BC2DAB CDFFFC89 2FCDAFD6 ,35.430 ns,0005.477338100060s,,,,,,,,,,,,,,,,,,,,,,,
# ,1,Upstream,,,MWr(64),,1981,,,,,,,,,,,,,,,,,2,184:00:0,0,,00001F40:42826200,,,1111,1111,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0x13527BEB,,,DB210000 1C000000 ,1.500 ns,0005.477338138060s,,,,,,,,,,,,,,,,,,,,,,,
# ,2,Upstream,,,MWr(64),,1982,,,,,,,,,,,,,,,,,32,184:00:0,0,,00001F00:0000CB80,,,1111,1111,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0xBE68CE7C,,,37B40676 978A80B0 BE75959B CF4A7791 D84DFC7D 9BC8A17C 02C2E3F3 B33DDBFF 2521CF95 D0839C4C C3593B40 02A4664B D1D53363 B5DBB628 F548C08B DA9A0BD9 B27141E0 A9879D00 3D0C77BD E5CAE0C2 5BE03CAC 4090C436 E686543D 62148A1C 4117C99E 71430C38 405325BC A654E6DF FF5D21BB B0434083 4BC3F6ED 04896886 ,0.940 ns,0005.477338140060s,,,,,,,,,,,,,,,,,,,,,,,
# ,3,Downstream,,ACK,,,,1979,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0x7073,,3.310 ns,0005.477338141000s,,,,,,,,,,,,,,,,,,,,,,,
#
# Details of different fields:
# 'DATA' is in hex format, without a '0x' prefix, grouped into dword quantities
# 'Length' is in dwords
#
# What to analyze: 
# Only analyze packets of 'TLP Type' = 'MWr(64)' and 'Link Dir' = 'Upstream'
# Show the relationships between the following:
# 1. First word of data of 2-dword writes vs. sequence number
# 2. Address bits 15:7 of 32-dword writes vs. sequence number
# 3. First word of data of 2-dword writes vs. address 15:7 of the 32-dword writes
# 4. Last qword of data of 32-dword writes vs. sequence number
# 5. First qword of data of 32-dword writes vs. sequence number
# 6. First qword of data of 32-dword writes vs. last qword of data of 32-dword writes
# 7. Last qword of data of 32-dword writes vs. address bits 15:7 of the 32-dword writes
#
# Files to analyze:
# traces/csv/GPUtoGPU_H100_P2P_NVBandwidthWriteSM_RequesterSide_with_data.csv

# This script reads a csv file representing a PCIe trace and analyzes the relationships of the DATA fields 
# The script presents charts, plots, and/or tables summarizing the patterns in the DATA field

import pandas as pd
import numpy as np
import os
import tempfile
import shutil
import glob
import logging
import holoviews as hv
from holoviews import opts
import holoviews.operation.datashader as hd
import panel as pn
import imageio.v2 as imageio
from bokeh.io import export_png
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

hv.extension('bokeh')
hv.renderer('bokeh').theme = 'dark_minimal'

def apply_light_background(plot, element):
    """Force a light background and dark text/grid colors for a specific plot."""
    fig = plot.state
    fig.background_fill_color = 'white'
    fig.border_fill_color = 'white'
    fig.outline_line_color = 'black'
    fig.title.text_color = 'black'
    fig.xaxis.axis_label_text_color = 'black'
    fig.yaxis.axis_label_text_color = 'black'
    fig.xaxis.major_label_text_color = 'black'
    fig.yaxis.major_label_text_color = 'black'
    fig.xgrid.grid_line_color = '#D0D0D0'
    fig.ygrid.grid_line_color = '#D0D0D0'

# Define a 6-color palette following the colors of the rainbow
SIX_COLOR_PALETTE = ['#FF4500', '#FFD700', '#32CD32', '#00FFFF', "#0A2AFBFF", '#8A2BE2']

# Define a 33-color palette in a rainbow-like gradient
THIRTYTHREE_COLOR_PALETTE = [
    '#5B5280','#6074AB','#74A0D1','#95C3E9','#C0E5F3','#FAFFE0','#E3E0D7','#C3B8B1',
    '#A39391','#8D7176','#6A4C62','#4E3161','#421E42','#612447','#7A3757','#96485B',
    '#BD6868','#D18B79','#DBAC8C','#E6CFA1','#E7EBBC','#B2DBA0','#87C293','#70A18F',
    '#637C8F','#B56E75','#C98F8F','#DFB6AE','#EDD5CA','#D5A3A6', '#BD7182','#9E5476','#753C6A'
]

def parse_data_field(data_string):
    """Parse the DATA field from the csv file and convert to list of integers."""
    if pd.isna(data_string) or data_string == '':
        return []
    
    try:
        # Remove any prefixes and whitespace
        clean_data = data_string.replace('0x', '').strip()
        
        # Split by whitespace to get dwords
        dwords = clean_data.split()
        
        # Convert each dword from hex to int
        return [int(dword, 16) for dword in dwords]
    except ValueError:
        # If conversion fails, return empty list
        return []

def parse_address(address_string):
    """Parse the Address field and extract the lower 16 bits."""
    if pd.isna(address_string) or address_string == '':
        return None
    
    try:
        # Split by colon and get the second part
        parts = address_string.split(':')
        if len(parts) < 2:
            return None
        
        # Get the lower 16 bits (4 hex digits)
        lower_addr_hex = parts[1][-4:] if len(parts[1]) >= 4 else parts[1]
        return int(lower_addr_hex, 16)
    except (ValueError, IndexError):
        return None

def _find_chrome_binary():
    """Best-effort discovery of a Chrome/Chromium executable on Windows/Linux."""
    env_candidates = [
        os.environ.get('CHROME_BIN'),
        os.environ.get('GOOGLE_CHROME_BIN')
    ]
    path_candidates = [
        shutil.which('chrome'),
        shutil.which('google-chrome'),
        shutil.which('chromium'),
        shutil.which('chromium-browser')
    ]
    windows_candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
        r'C:\Program Files\Chromium\Application\chrome.exe'
    ]

    for candidate in env_candidates + path_candidates + windows_candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return None

def _find_chromedriver_binary():
    """Best-effort discovery of a local chromedriver binary."""
    env_candidate = os.environ.get('CHROMEDRIVER')
    if env_candidate and os.path.exists(env_candidate):
        return env_candidate

    path_candidate = shutil.which('chromedriver')
    if path_candidate and os.path.exists(path_candidate):
        return path_candidate

    user_profile = os.path.expandvars(r'%USERPROFILE%')
    wdm_pattern = os.path.join(
        user_profile,
        '.wdm',
        'drivers',
        'chromedriver',
        'win64',
        '*',
        'chromedriver-win32',
        'chromedriver.exe'
    )
    wdm_candidates = sorted(glob.glob(wdm_pattern), reverse=True)
    if wdm_candidates:
        return wdm_candidates[0]

    return None

def _configure_webdriver_proxy_bypass():
    """Ensure localhost webdriver traffic does not go through corporate proxies."""
    localhost_bypass = 'localhost,127.0.0.1'
    existing = os.environ.get('NO_PROXY', '')
    if localhost_bypass not in existing:
        os.environ['NO_PROXY'] = f"{existing},{localhost_bypass}".strip(',')
    existing_lower = os.environ.get('no_proxy', '')
    if localhost_bypass not in existing_lower:
        os.environ['no_proxy'] = f"{existing_lower},{localhost_bypass}".strip(',')

def _build_chrome_webdriver():
    """Create a Chrome webdriver robustly for bokeh export_png."""
    _configure_webdriver_proxy_bypass()

    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument('--proxy-server=direct://')
    chrome_options.add_argument('--proxy-bypass-list=*')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--force-device-scale-factor=1')
    chrome_options.add_argument('--window-size=2400,1200')

    chrome_binary = _find_chrome_binary()
    if chrome_binary:
        chrome_options.binary_location = chrome_binary
        print(f"Using Chrome binary: {chrome_binary}")
    else:
        print("Warning: Chrome binary not auto-detected. Trying Selenium defaults.")

    # 1) Use an already-available local chromedriver first
    local_driver = _find_chromedriver_binary()
    if local_driver:
        try:
            print(f"Using local ChromeDriver: {local_driver}")
            return webdriver.Chrome(service=Service(local_driver), options=chrome_options)
        except WebDriverException as e:
            print(f"Warning: Local ChromeDriver startup failed: {e}")

    # 2) Try webdriver-manager downloaded driver
    try:
        driver_path = ChromeDriverManager().install()
        print(f"Using webdriver-manager ChromeDriver: {driver_path}")
        return webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    except Exception as e:
        print(f"Warning: webdriver-manager setup failed: {e}")

    # 3) Fallback to Selenium Manager automatic setup
    try:
        print("Trying Selenium Manager automatic Chrome setup...")
        return webdriver.Chrome(options=chrome_options)
    except Exception as e:
        raise RuntimeError(
            "Unable to start Chrome webdriver for export_png. "
            "Set CHROMEDRIVER to a valid chromedriver executable path or install Google Chrome. "
            f"Last error: {e}"
        )

def save_holoviews_frames_as_gif(frames, gif_path, duration=0.12):
    """Render HoloViews frame objects to PNG and stitch into an animated GIF."""
    if not frames:
        return None

    temp_dir = tempfile.mkdtemp(prefix='plot16_frames_')
    png_paths = []
    driver = None
    export_logger = logging.getLogger('bokeh.io.export')
    original_export_log_level = export_logger.level
    try:
        export_logger.setLevel(logging.ERROR)
        driver = _build_chrome_webdriver()
        renderer = hv.renderer('bokeh')

        for frame_idx, frame_obj in frames:
            bokeh_fig = renderer.get_plot(frame_obj).state
            png_path = os.path.join(temp_dir, f'frame_{frame_idx:03d}.png')
            export_png(bokeh_fig, filename=png_path, webdriver=driver)
            png_paths.append(png_path)

        if not png_paths:
            return None

        images = [imageio.imread(path) for path in png_paths]
        imageio.mimsave(gif_path, images, duration=duration, loop=0)
        return gif_path
    except Exception as e:
        print(f"Warning: Unable to generate GIF at {gif_path}: {e}")
        return None
    finally:
        export_logger.setLevel(original_export_log_level)
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

def load_and_filter_data(file_path):
    """Load and filter the CSV file."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return None
            
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Filter for MWr(64) Upstream packets
        filtered_df = df[(df['TLP Type'] == 'MWr(64)') & (df['Link Dir'] == 'Upstream')].copy()
        
        if filtered_df.empty:
            print(f"No MWr(64) Upstream packets found in {file_path}")
            return None
        
        # Parse the DATA field
        filtered_df['DATA_parsed'] = filtered_df['DATA'].apply(parse_data_field)
        
        # Add column for number of dwords in DATA
        filtered_df['DATA_dword_count'] = filtered_df['DATA_parsed'].apply(len)
        
        # Parse address field to extract lower 16 bits
        filtered_df['Address_lower_16bits'] = filtered_df['Address'].apply(parse_address)
        
        # Convert 'Time Stamp' to numeric for sequence analysis
        filtered_df['Time Stamp'] = pd.to_numeric(filtered_df['Time Stamp'].str.replace('s', ''), errors='coerce')
        
        # Sort by timestamp to ensure correct sequence
        filtered_df = filtered_df.sort_values('Time Stamp')
        
        # Add a sequence number for tracking transaction order
        filtered_df['seq_num'] = range(len(filtered_df))

        return filtered_df
    
    except Exception as e:
        print(f"Error loading or processing file {file_path}: {e}")
        return None

def extract_analysis_sets(df):
    results = {}
    if df is None or df.empty:
        return results

    # Extract the length distribution
    length_counts = df['DATA_dword_count'].value_counts().sort_index()
    length_distribution = pd.DataFrame({
        'Length': length_counts.index,
        'Count': length_counts.values
    })
    results['length_distribution'] = length_distribution

    # analyzing 2-dword writes
    dw2 = df[df['Length'] == 2].copy()
    if not dw2.empty:
        dw2['first_word'] = dw2['DATA_parsed'].apply(lambda x: (x[0] >> 16) & 0xFFFF if len(x) > 0 else None)
        # Extract individual data bits 15:7
        for bit in range(7, 16):
            dw2[f'data_bit_{bit}'] = dw2['first_word'].apply(lambda x: (x >> bit) & 1 if pd.notna(x) else None)
        results['dw2'] = dw2
        # convert first_word from little-endian to big-endian
        dw2['first_word_big_endian'] = dw2['first_word'].apply(lambda x: ((x & 0xFF) << 8) | ((x & 0xFF00) >> 8) if pd.notna(x) else None)
        # find the smallest and largest values in the first_word column
        min_first_word = dw2['first_word_big_endian'].min()
        max_first_word = dw2['first_word_big_endian'].max()
        if not pd.notna(min_first_word) or not pd.notna(max_first_word):
            print("Warning: Unable to find min or max first word values. Aborting further analysis.")
            return results

        # print some statistics about the first word
        print(f"Analyzing 2-dword writes:")
        print(f"Number of 2-dword writes: {len(dw2)}")
        print(f"Minimum first word: 0x{min_first_word:04X}")
        print(f"Maximum first word: 0x{max_first_word:04X}")
        print(f"Range of first word: {max_first_word - min_first_word:04X}")

        dw2['normalized_first_word'] = dw2['first_word_big_endian'] - min_first_word if pd.notna(min_first_word) else dw2['first_word_big_endian']
        # create a column for the remainder when dividing the normalized first word by 6
        dw2['remainder_6'] = dw2['normalized_first_word'] % 6

        # Map remainder_6 to color
        dw2['color'] = dw2['remainder_6'].apply(lambda x: SIX_COLOR_PALETTE[int(x)] if pd.notna(x) else '#CCCCCC')

        # --- Enhancement: Count bit 0 of first_word_big_endian ---
        dw2['bit0'] = dw2['first_word_big_endian'].apply(lambda x: (int(x) & 1) if pd.notna(x) else None)
        bit0_0_count = dw2['bit0'].eq(0).sum()
        bit0_1_count = dw2['bit0'].eq(1).sum()
        results['dw2_bit0_0_count'] = int(bit0_0_count)
        results['dw2_bit0_1_count'] = int(bit0_1_count)

    # analyzing 32-dword writes
    dw32 = df[df['Length'] == 32].copy()
    if not dw32.empty:
        dw32['Address_bits_15_7'] = dw32['Address_lower_16bits'].apply(
            lambda x: (x >> 7) & 0x1FF if pd.notna(x) else None
        )
        # Extract individual address bits 15:7
        for bit in range(7, 16):
            dw32[f'addr_bit_{bit}'] = dw32['Address_lower_16bits'].apply(lambda x: (x >> bit) & 1 if pd.notna(x) else None)
        dw32['first_qword'] = dw32['DATA_parsed'].apply(
            lambda x: ((x[0] << 32) | x[1]) if len(x) > 1 else None
        )
        dw32['last_qword'] = dw32['DATA_parsed'].apply(
            lambda x: ((x[-2] << 32) | x[-1]) if len(x) > 1 else None
        )
        results['dw32'] = dw32
        # create a column for the remainder when dividing the address bits 15:7 by 6
        dw32['remainder_6'] = dw32['Address_bits_15_7'] % 6

        # --- Enhancement: Count bit 7 of address ---
        dw32['addr_bit_7'] = dw32['Address_lower_16bits'].apply(lambda x: (int(x) >> 7) & 1 if pd.notna(x) else None)
        addr_bit7_0_count = dw32['addr_bit_7'].eq(0).sum()
        addr_bit7_1_count = dw32['addr_bit_7'].eq(1).sum()
        results['dw32_addr_bit7_0_count'] = int(addr_bit7_0_count)
        results['dw32_addr_bit7_1_count'] = int(addr_bit7_1_count)

    # The actual byte size for the copy is calculated using the formula: 
    # (threadsPerBlock * deviceSMCount) * floor(copySize / (threadsPerBlock * deviceSMCount)). 
    # The threadsPerBlock value is set to 512. 
    # The total number of threads launched depends on the deviceSMCount, 
    # which represents the number of SMs available on the device, and the size of the copy. 

    return results

def plot_relationships(results, output_dir, plot_heights, enable_plot):
    output_paths = []
    dw2 = results.get('dw2', pd.DataFrame())
    dw32 = results.get('dw32', pd.DataFrame())

    # 16. Animated histogram: Number of occurrences of each first_word_big_endian value for each time bin (not cumulative)
    if not dw2.empty and 16 in enable_plot:
        # Create time bins (e.g., 100 bins)
        n_bins = 100
        time_min = dw2['Time Stamp'].min()
        time_max = dw2['Time Stamp'].max()
        time_bins = np.linspace(time_min, time_max, n_bins + 1)

        # Assign each row to a time bin
        dw2['time_bin'] = pd.cut(dw2['Time Stamp'], bins=time_bins, labels=False, include_lowest=True)

        # Find all unique first_word_big_endian values across all bins, sorted
        all_fw_values = sorted(dw2['first_word_big_endian'].dropna().unique())
        color_map = {fw: THIRTYTHREE_COLOR_PALETTE[i % len(THIRTYTHREE_COLOR_PALETTE)] for i, fw in enumerate(all_fw_values)}

        # Prepare frame data for animation (sliding window of 10 bins)
        frame_dfs = []
        global_count_max = 0
        for bin_idx in range(n_bins):
            # Select the current and previous 10 bins
            if bin_idx < 10:
                frame_df = dw2[dw2['time_bin'].isin(range(0, bin_idx + 1))]
            else:
                frame_df = dw2[dw2['time_bin'].isin(range(bin_idx - 9, bin_idx + 1))]
            counts = frame_df['first_word_big_endian'].value_counts().sort_index()
            if counts.empty:
                continue
            # Ensure all_fw_values are present in every frame (fill missing with 0)
            frame_data = []
            for fw in all_fw_values:
                frame_data.append({
                    'first_word_big_endian': fw,
                    'count': counts.get(fw, 0),
                    'color': color_map[fw]
                })
            fw_hist_df = pd.DataFrame(frame_data)
            global_count_max = max(global_count_max, int(fw_hist_df['count'].max()))
            frame_dfs.append((bin_idx, fw_hist_df))

        # Build frames with fixed y-scale across all bins
        fixed_ylim = (0, max(1, global_count_max))
        frames = []
        for bin_idx, fw_hist_df in frame_dfs:
            bars = hv.Bars(
                fw_hist_df, kdims=['first_word_big_endian'], vdims=['count', 'color']
            ).opts(
                opts.Bars(
                    title=f'Occurrences of Each First Word Value (2-DW Writes) - Time Bin {bin_idx+1}/{n_bins}',
                    color='color', 
                    line_color=None,
                    width=2300, height=800,
                    xlabel='First Word (16 bits)', ylabel='Count',
                    ylim=fixed_ylim,
                    tools=['hover'],
                    hooks=[apply_light_background]
                )
            )
            frames.append((bin_idx, bars))

        # Create HoloMap for animation
        anim = hv.HoloMap(dict(frames), kdims='Time Bin')
        out_anim = os.path.join(output_dir, 'anim_hist_2dw_firstword_occurrences.html')
        pn.panel(anim).save(out_anim, embed=True)
        output_paths.append(out_anim)
        plot_heights['anim_hist_2dw_firstword_occurrences.html'] = 800

        out_gif = os.path.join(output_dir, 'anim_hist_2dw_firstword_occurrences.gif')
        gif_path = save_holoviews_frames_as_gif(frames, out_gif, duration=0.12)
        if gif_path is not None:
            print(f"Animated GIF written to: {gif_path}")

    # 19. Animated histogram (grouped x-axis): like plot 16, but 50 time bins and first_word_big_endian grouped into size-33 buckets
    if not dw2.empty and 19 in enable_plot:
        # Create time bins (50 bins)
        n_bins = 50
        time_min = dw2['Time Stamp'].min()
        time_max = dw2['Time Stamp'].max()
        time_bins = np.linspace(time_min, time_max, n_bins + 1)

        # Assign each row to a time bin
        dw2['time_bin_19'] = pd.cut(dw2['Time Stamp'], bins=time_bins, labels=False, include_lowest=True)

        fw_min = int(dw2['first_word_big_endian'].min())
        # Group first_word_big_endian values into buckets of size 33:
        # group 1 => [fw_min .. fw_min+32], group 2 => [fw_min+33 .. fw_min+65], etc.
        dw2['first_word_big_endian_group33'] = dw2['first_word_big_endian'].apply(
            lambda x: ((int(x) - fw_min) // 33) + 1 if pd.notna(x) else None
        )

        all_fw_group_values = sorted(dw2['first_word_big_endian_group33'].dropna().unique())
        color_map = {
            fw: THIRTYTHREE_COLOR_PALETTE[i % len(THIRTYTHREE_COLOR_PALETTE)]
            for i, fw in enumerate(all_fw_group_values)
        }

        # Prepare frame data for animation (sliding window of 10 bins)
        frame_dfs = []
        global_count_max = 0
        for bin_idx in range(n_bins):
            if bin_idx < 10:
                frame_df = dw2[dw2['time_bin_19'].isin(range(0, bin_idx + 1))]
            else:
                frame_df = dw2[dw2['time_bin_19'].isin(range(bin_idx - 9, bin_idx + 1))]

            counts = frame_df['first_word_big_endian_group33'].value_counts().sort_index()
            if counts.empty:
                continue

            frame_data = []
            for fw in all_fw_group_values:
                frame_data.append({
                    'first_word_big_endian_group33': fw,
                    'count': counts.get(fw, 0),
                    'color': color_map[fw]
                })

            fw_hist_df = pd.DataFrame(frame_data)
            global_count_max = max(global_count_max, int(fw_hist_df['count'].max()))
            frame_dfs.append((bin_idx, fw_hist_df))

        # Build frames with fixed y-scale across all bins
        fixed_ylim = (0, max(1, global_count_max))
        frames = []
        for bin_idx, fw_hist_df in frame_dfs:
            bars = hv.Bars(
                fw_hist_df, kdims=['first_word_big_endian_group33'], vdims=['count', 'color']
            ).opts(
                opts.Bars(
                    title=f'Occurrences by First Word Group (size 33) (2-DW Writes) - Time Bin {bin_idx+1}/{n_bins}',
                    color='color',
                    line_color=None,
                    width=800, height=800,
                    xlabel='First Word Group (size 33 buckets)', ylabel='Count',
                    ylim=fixed_ylim,
                    tools=['hover'],
                    hooks=[apply_light_background]
                )
            )
            frames.append((bin_idx, bars))

        # Create HoloMap for animation
        anim = hv.HoloMap(dict(frames), kdims='Time Bin')
        out_anim = os.path.join(output_dir, 'anim_hist_2dw_firstword_occurrences_group33.html')
        pn.panel(anim).save(out_anim, embed=True)
        output_paths.append(out_anim)
        plot_heights['anim_hist_2dw_firstword_occurrences_group33.html'] = 800

        out_gif = os.path.join(output_dir, 'anim_hist_2dw_firstword_occurrences_group33.gif')
        gif_path = save_holoviews_frames_as_gif(frames, out_gif, duration=0.12)
        if gif_path is not None:
            print(f"Animated GIF written to: {gif_path}")

    # 17. Animated histogram: Number of occurrences of each address bits 15:7 value for each time bin (not cumulative)
    if not dw32.empty and 17 in enable_plot:
        # Create time bins (e.g., 100 bins)
        n_bins = 100
        time_min = dw32['Time Stamp'].min()
        time_max = dw32['Time Stamp'].max()
        time_bins = np.linspace(time_min, time_max, n_bins + 1)

        # Assign each row to a time bin
        dw32['time_bin'] = pd.cut(dw32['Time Stamp'], bins=time_bins, labels=False, include_lowest=True)

        # Find all unique address bits 15:7 values across all bins, sorted
        all_addr_values = sorted(dw32['Address_bits_15_7'].dropna().unique())
        color_map = {addr: THIRTYTHREE_COLOR_PALETTE[i % len(THIRTYTHREE_COLOR_PALETTE)] for i, addr in enumerate(all_addr_values)}

        # Prepare frames for animation (sliding window of 10 bins)
        frames = []
        for bin_idx in range(n_bins):
            # Select the current and previous 10 bins
            if bin_idx < 10:
                frame_df = dw32[dw32['time_bin'].isin(range(0, bin_idx + 1))]
            else:
                frame_df = dw32[dw32['time_bin'].isin(range(bin_idx - 9, bin_idx + 1))]
            counts = frame_df['Address_bits_15_7'].value_counts().sort_index()
            if counts.empty:
                continue
            # Ensure all_addr_values are present in every frame (fill missing with 0)
            frame_data = []
            for addr in all_addr_values:
                frame_data.append({
                    'Address_bits_15_7': addr,
                    'count': counts.get(addr, 0),
                    'color': color_map[addr]
                })
            addr_hist_df = pd.DataFrame(frame_data)
            bars = hv.Bars(
                addr_hist_df, kdims=['Address_bits_15_7'], vdims=['count', 'color']
            ).opts(
                opts.Bars(
                    title=f'Occurrences of Each Address Bits 15:7 Value (32-DW Writes) - Time Bin {bin_idx+1}/{n_bins}',
                    color='color', 
                    width=2300, height=800,
                    xlabel='Address Bits 15:7', ylabel='Count',
                    tools=['hover']
                )
            )
            frames.append((bin_idx, bars))

        # Create HoloMap for animation
        anim = hv.HoloMap(dict(frames), kdims='Time Bin')
        out_anim = os.path.join(output_dir, 'anim_hist_32dw_addr_occurrences.html')
        pn.panel(anim).save(out_anim, embed=True)
        output_paths.append(out_anim)
        plot_heights['anim_hist_32dw_addr_occurrences.html'] = 800

    # 18. Animation: For each 32DW write with address bit n = 0, time to closest 32DW write with same address but bit n = 1 (forward or backward)
    if not dw32.empty and 18 in enable_plot:
        n_bins = 100
        n_samples = 10  # Number of samples to take from each bin
        global_ymax = 2000 # y-axis max, in ns
        time_min = dw32['Time Stamp'].min()
        time_max = dw32['Time Stamp'].max()
        time_bins = np.linspace(time_min, time_max, n_bins + 1)
        dw32['time_bin'] = pd.cut(dw32['Time Stamp'], bins=time_bins, labels=False, include_lowest=True)
        valid_dw32 = dw32.dropna(subset=['Time Stamp'])

        # --- Compute global y-axis max for all bins and all bits ---
        all_time_deltas_by_bit = {bit: [] for bit in range(7, 16)}
        for bit in range(7, 16):
            mask = valid_dw32[f'addr_bit_{bit}'] == 0
            for bin_idx in range(n_bins):
                bin_df = valid_dw32[valid_dw32['time_bin'] == bin_idx]
                bit0_df = bin_df[bin_df[f'addr_bit_{bit}'] == 0]
                if len(bit0_df) > n_samples:
                    bit0_df = bit0_df.sample(n=n_samples, random_state=42)
                for idx, row in bit0_df.iterrows():
                    # Mask out the bit under test
                    addr_mask = ~(1 << bit)
                    addr = row['Address_lower_16bits'] & addr_mask
                    t0 = row['Time Stamp']
                    candidates = valid_dw32[
                        (valid_dw32['Address_lower_16bits'] & addr_mask == addr) &
                        (valid_dw32[f'addr_bit_{bit}'] == 1)
                    ]
                    if not candidates.empty:
                        time_diffs = np.abs(candidates['Time Stamp'] - t0)
                        min_idx = time_diffs.idxmin()
                        t1 = candidates.loc[min_idx, 'Time Stamp']
                        all_time_deltas_by_bit[bit].append(abs(t1 - t0) * 1e9)

        # --- Create frames for each bit ---
        for bit in range(7, 16):
            frames = []
            for bin_idx in range(n_bins):
                bin_df = valid_dw32[valid_dw32['time_bin'] == bin_idx]
                bit0_df = bin_df[bin_df[f'addr_bit_{bit}'] == 0]
                if len(bit0_df) > n_samples:
                    bit0_df = bit0_df.sample(n=n_samples, random_state=42)
                time_deltas = []
                for idx, row in bit0_df.iterrows():
                    addr_mask = ~(1 << bit)
                    addr = row['Address_lower_16bits'] & addr_mask
                    t0 = row['Time Stamp']
                    candidates = valid_dw32[
                        (valid_dw32['Address_lower_16bits'] & addr_mask == addr) &
                        (valid_dw32[f'addr_bit_{bit}'] == 1)
                    ]
                    if not candidates.empty:
                        time_diffs = np.abs(candidates['Time Stamp'] - t0)
                        min_idx = time_diffs.idxmin()
                        t1 = candidates.loc[min_idx, 'Time Stamp']
                        time_deltas.append(abs(t1 - t0) * 1e9)
                if time_deltas:
                    avg_time = min(float(np.mean(time_deltas)), global_ymax)
                    median_time = min(float(np.median(time_deltas)), global_ymax)
                    min_time = min(float(np.min(time_deltas)), global_ymax)
                else:
                    avg_time = median_time = min_time = np.nan
                stats_df = pd.DataFrame({
                    'stat': ['avg', 'median', 'min'],
                    'value': [avg_time, median_time, min_time]
                })
                color_map = {'avg': '#00FFFF', 'median': '#FFD700', 'min': '#32CD32'}
                stats_df['color'] = stats_df['stat'].map(color_map)
                points = hv.Scatter(
                    stats_df, kdims=['stat'], vdims=['value', 'color']
                ).opts(
                    opts.Scatter(
                        color='color',
                        size=20,
                        width=2300, height=800,
                        title=f'Time to Closest Bit{bit}=1 Write (Bin {bin_idx+1}/{n_bins})',
                        xlabel='Statistic', ylabel='Time (ns)',
                        tools=['hover'],
                        ylim=(0, global_ymax)
                    )
                )
                frames.append((bin_idx, points))
            anim = hv.HoloMap(dict(frames), kdims='Time Bin')
            out_anim = os.path.join(output_dir, f'anim_time_to_closest_bit{bit}_1.html')
            pn.panel(anim).save(out_anim, embed=True)
            output_paths.append(out_anim)
            plot_heights[f'anim_time_to_closest_bit{bit}_1.html'] = 800

    return output_paths

def generate_summary_report(results, output_paths, plot_heights, output_dir):
    """Generate an HTML summary report linking to all plots."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PCIe Trace Analysis Report (HoloViews)</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            h2 { color: #3498db; }
            h3 { color: #2980b9; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .plot-link { margin-bottom: 10px; }
            .plot-section { margin-top: 20px; }
            iframe { border: 1px solid #ddd; margin: 10px 0; width: 100%; min-height: 840px; }
        </style>
    </head>
    <body>
        <h1>PCIe Trace Analysis Report (HoloViews)</h1>
    """
    
    # Add summary statistics
    html_content += "<h2>Summary Statistics</h2>"
    html_content += "<table>"
    html_content += "<tr><th>Metric</th><th>Value</th></tr>"
    
    if 'length_distribution' in results:
        # total packets
        total_packets = sum(results['length_distribution'].Count)
        html_content += f"<tr><td>Total MWr(64) Upstream Packets</td><td>{total_packets}</td></tr>"
        # count of packets by length
        html_content += "<tr><td colspan='2'>Length Distribution of Packets</td></tr>"
        html_content += "<tr><th>Length</th><th>Count</th></tr>"
        for _, row in results['length_distribution'].iterrows():
            html_content += f"<tr><td>{row['Length']}</td><td>{row['Count']}</td></tr>"
    else:
        html_content += "<tr><td colspan='2'>No length distribution data available.</td></tr>"
    
    html_content += "</table>"
    
    # --- Enhancement: Add bit summary table ---
    html_content += "<h2>Bitwise Summary Table</h2>"
    html_content += "<table>"
    html_content += "<tr><th>Category</th><th>Bit Value</th><th>Count</th></tr>"
    # 2DW writes, bit 0 of first_word_big_endian
    html_content += "<tr><td>2DW writes, first_word_big_endian bit 0</td><td>0</td><td>{}</td></tr>".format(results.get('dw2_bit0_0_count', 0))
    html_content += "<tr><td>2DW writes, first_word_big_endian bit 0</td><td>1</td><td>{}</td></tr>".format(results.get('dw2_bit0_1_count', 0))
    # 32DW writes, bit 7 of address
    html_content += "<tr><td>32DW writes, address bit 7</td><td>0</td><td>{}</td></tr>".format(results.get('dw32_addr_bit7_0_count', 0))
    html_content += "<tr><td>32DW writes, address bit 7</td><td>1</td><td>{}</td></tr>".format(results.get('dw32_addr_bit7_1_count', 0))
    html_content += "</table>"

    # Embed all plots as iframes
    html_content += "<h2>Interactive Analysis Plots</h2>"
    
    if output_paths:
        html_content += "<div class='plot-section'>"
        html_content += "<h3>Basic Distribution Analysis</h3>"
        for path in output_paths:
            plot_name = os.path.basename(path)
            # Plot heights are stored in a dict, so look them up here.
            if plot_name in plot_heights:
                iframe_height = plot_heights[plot_name]+40  # add some padding for margin
            else:
                iframe_height = 640  # fallback default

            html_content += f'<div class="plot-link"><iframe src="{plot_name}" height="{iframe_height}"></iframe></div>'
        html_content += "</div>"
    else:
        html_content += "<p>No plots generated. Please check the analysis steps.</p>"
      
    html_content += """
    </body>
    </html>
    """
    
    report_path = os.path.join(output_dir, 'analysis_report.html')
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path

def main():
    enable_plot = {19}  # Set of plot numbers to enable
    plot_heights = {} # Set plot heights in plot_relationships function
    print("Starting PCIe Trace Analysis with HoloViews...")
    input_file = 'traces/csv/huge/GPUtoGPU_H100_P2P_NVBandwidthWriteSM_RequesterSide_compressed.csv'
    output_dir = 'reports'
    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading and filtering data from {input_file}...")
    df = load_and_filter_data(input_file)
    if df is None or df.empty:
        print("No valid data to analyze. Exiting.")
        return
    results = extract_analysis_sets(df)
    print("Generating relationship plots...")
    output_paths = plot_relationships(results, output_dir, plot_heights, enable_plot)
    print("Generating summary report...")
    report_path = generate_summary_report(results, output_paths, plot_heights, output_dir)
    print(f"Analysis complete. Summary report available at: {report_path}")

if __name__ == "__main__":
    main()

# %%