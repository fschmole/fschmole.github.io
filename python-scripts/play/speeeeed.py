#!/usr/bin/env python3
"""
speeeeed.py - Speed up GPX tracks by adjusting timestamps proportionally to distance.

Usage:
    python speeeeed.py input.gpx --speedup 20 --output output.gpx
    python speeeeed.py input.gpx --speedup 20 --shift-to-now --output output.gpx
    python speeeeed.py input.gpx --target-pace 7:30 --output output.gpx
    python speeeeed.py input.gpx --target-pace 8:15 --shift-to-now --output output.gpx
"""

import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import sys


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the earth (in meters).
    
    Args:
        lat1, lon1: Latitude and longitude of point 1 in degrees
        lat2, lon2: Latitude and longitude of point 2 in degrees
    
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r


def parse_gpx_time(time_str):
    """Parse GPX timestamp string to datetime object."""
    # Handle both with and without microseconds
    try:
        return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def format_gpx_time(dt):
    """Format datetime object to GPX timestamp string."""
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_pace(pace_str):
    """
    Parse pace string in mm:ss format to seconds per mile.
    
    Args:
        pace_str: Pace string in format 'mm:ss' (e.g., '7:30')
    
    Returns:
        Seconds per mile as float
    """
    try:
        parts = pace_str.split(':')
        if len(parts) != 2:
            raise ValueError("Pace must be in mm:ss format")
        minutes = int(parts[0])
        seconds = int(parts[1])
        if minutes < 0 or seconds < 0 or seconds >= 60:
            raise ValueError("Invalid pace values")
        return minutes * 60 + seconds
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid pace format '{pace_str}'. Use mm:ss format (e.g., '7:30')")


def speed_up_gpx(input_file, speedup_percent=None, target_pace=None, shift_to_now=False, keep_finish=False, output_file=None):
    """
    Speed up a GPX track by adjusting timestamps proportionally to distance.
    
    Args:
        input_file: Path to input GPX file
        speedup_percent: Percentage to speed up (e.g., 20 = 20% faster)
        target_pace: Target pace in seconds per mile (mutually exclusive with speedup_percent)
        shift_to_now: If True, shift all timestamps so the last one is current time
        keep_finish: If True, keep the original finish time (shift start time backward)
        output_file: Path to output GPX file (if None, will be input_file with _fast suffix)
    """
    # Parse the GPX file
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Define namespace
    ns = {'': 'http://www.topografix.com/GPX/1/1'}
    ET.register_namespace('', ns[''])
    ET.register_namespace('gpxtpx', 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1')
    ET.register_namespace('gpxx', 'http://www.garmin.com/xmlschemas/GpxExtensions/v3')
    ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    
    # Find all track points
    trkpts = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
    
    if len(trkpts) < 2:
        print("Error: GPX file must contain at least 2 track points", file=sys.stderr)
        sys.exit(1)
    
    # Extract data from track points
    points = []
    for trkpt in trkpts:
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        time_elem = trkpt.find('{http://www.topografix.com/GPX/1/1}time')
        if time_elem is not None:
            time = parse_gpx_time(time_elem.text)
            points.append({
                'element': trkpt,
                'time_element': time_elem,
                'lat': lat,
                'lon': lon,
                'time': time
            })
    
    if len(points) < 2:
        print("Error: GPX file must contain at least 2 track points with timestamps", file=sys.stderr)
        sys.exit(1)
    
    # Calculate distances between consecutive points
    total_distance = 0
    for i in range(1, len(points)):
        distance = haversine_distance(
            points[i-1]['lat'], points[i-1]['lon'],
            points[i]['lat'], points[i]['lon']
        )
        points[i]['distance_from_start'] = total_distance + distance
        total_distance += distance
    points[0]['distance_from_start'] = 0
    
    # Calculate original duration
    original_start_time = points[0]['time']
    original_end_time = points[-1]['time']
    original_duration = (original_end_time - original_start_time).total_seconds()
    
    if original_duration <= 0:
        print("Error: Invalid time range in GPX file", file=sys.stderr)
        sys.exit(1)
    
    # Calculate new duration based on mode
    if target_pace is not None:
        # Calculate based on target pace (seconds per mile)
        distance_miles = total_distance / 1609.34  # Convert meters to miles
        new_duration = distance_miles * target_pace
        
        pace_minutes = int(target_pace // 60)
        pace_seconds = int(target_pace % 60)
        original_pace = (original_duration / 60) / distance_miles if distance_miles > 0 else 0
        
        print(f"Total distance: {total_distance:.1f} meters ({distance_miles:.2f} miles)")
        print(f"Original duration: {original_duration:.1f} seconds ({original_duration/60:.1f} minutes)")
        print(f"Original pace: {int(original_pace)}:{int((original_pace % 1) * 60):02d} min/mile")
        print(f"Target pace: {pace_minutes}:{pace_seconds:02d} min/mile")
        print(f"New duration: {new_duration:.1f} seconds ({new_duration/60:.1f} minutes)")
    else:
        # Calculate based on speedup percentage
        speed_factor = speedup_percent / 100.0
        new_duration = original_duration * (1 - speed_factor)
        
        print(f"Total distance: {total_distance:.1f} meters")
        print(f"Original duration: {original_duration:.1f} seconds ({original_duration/60:.1f} minutes)")
        print(f"New duration: {new_duration:.1f} seconds ({new_duration/60:.1f} minutes)")
        print(f"Speed increase: {speedup_percent}%")
    
    # Calculate new timestamps proportional to distance
    for point in points:
        if total_distance > 0:
            progress = point['distance_from_start'] / total_distance
        else:
            progress = 0
        
        new_time = original_start_time + timedelta(seconds=new_duration * progress)
        point['new_time'] = new_time
    
    # Apply time shift options
    if shift_to_now:
        current_time = datetime.utcnow()
        time_shift = current_time - points[-1]['new_time']
        
        print(f"Shifting timestamps so the last point is at current time: {format_gpx_time(current_time)}")
        
        for point in points:
            point['new_time'] += time_shift
    elif keep_finish:
        # Keep the original finish time by shifting backward
        time_shift = original_end_time - points[-1]['new_time']
        
        print(f"Keeping original finish time: {format_gpx_time(original_end_time)}")
        print(f"New start time: {format_gpx_time(points[0]['new_time'] + time_shift)}")
        
        for point in points:
            point['new_time'] += time_shift
    
    # Update the XML with new timestamps
    for point in points:
        point['time_element'].text = format_gpx_time(point['new_time'])
    
    # Update metadata time if it exists
    metadata_time = root.find('.//{http://www.topografix.com/GPX/1/1}metadata/{http://www.topografix.com/GPX/1/1}time')
    if metadata_time is not None:
        metadata_time.text = format_gpx_time(points[0]['new_time'])
    
    # Determine output filename
    if output_file is None:
        if input_file.endswith('.gpx'):
            output_file = input_file[:-4] + '_fast.gpx'
        else:
            output_file = input_file + '_fast.gpx'
    
    # Write the modified GPX file
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"\nOutput written to: {output_file}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Speed up GPX tracks by adjusting timestamps proportionally to distance.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Speed up a track by 20%%
  python speeeeed.py track.gpx --speedup 20

  # Speed up by 30%% and shift so the last timestamp is now
  python speeeeed.py track.gpx --speedup 30 --shift-to-now

  # Set target pace to 7:30 min/mile
  python speeeeed.py track.gpx --target-pace 7:30

  # Set target pace and shift to current time
  python speeeeed.py track.gpx --target-pace 8:15 --shift-to-now

  # Speed up but keep the original finish time
  python speeeeed.py track.gpx --speedup 20 --keep-finish

  # Specify custom output file
  python speeeeed.py track.gpx --speedup 25 --output faster_track.gpx
        """
    )
    
    parser.add_argument('input_file', help='Input GPX file')
    
    # Create mutually exclusive group for speedup vs target-pace
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--speedup', '-s', type=float,
                        help='Percentage to speed up (e.g., 20 for 20%% faster)')
    mode_group.add_argument('--target-pace', '-p', type=str,
                        help='Target pace in mm:ss format (e.g., 7:30 for 7:30 min/mile)')
    
    # Create mutually exclusive group for time shift options
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument('--shift-to-now', '-n', action='store_true',
                        help='Shift all timestamps so the last one is current time')
    time_group.add_argument('--keep-finish', '-k', action='store_true',
                        help='Keep the original finish time (shift start time backward instead)')
    
    parser.add_argument('--output', '-o', help='Output GPX file (default: input_file_fast.gpx)')
    
    args = parser.parse_args()
    
    # Validate and parse arguments
    target_pace_seconds = None
    speedup_percent = None
    
    if args.speedup is not None:
        if args.speedup < 0 or args.speedup >= 100:
            print("Error: speedup percentage must be between 0 and 100 (exclusive)", file=sys.stderr)
            sys.exit(1)
        speedup_percent = args.speedup
    else:
        try:
            target_pace_seconds = parse_pace(args.target_pace)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        speed_up_gpx(args.input_file, speedup_percent, target_pace_seconds, args.shift_to_now, args.keep_finish, args.output)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing GPX file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
