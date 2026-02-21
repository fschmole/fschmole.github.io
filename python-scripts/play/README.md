# Play Scripts

Fun scripts and personal experiments.

## Scripts

### [speeeeed.py](speeeeed.py)

Manipulates GPX track files by rewriting timestamps to artificially speed up a recorded activity. Timestamps are redistributed proportionally to distance between track points, so the adjusted track retains the original route geometry while appearing to have been completed faster (or at a specific target pace).

**Features:**
- Speed up a track by a percentage (`--speedup`)
- Target a specific pace in `mm:ss` per mile (`--target-pace`)
- Shift all timestamps so the activity ends at the current time (`--shift-to-now`)
- Preserve the original finish time, shifting the start backward instead (`--keep-finish`)

**Requirements:** Python 3.9+, no third-party dependencies.

**Usage:**
```bash
# Speed up a track by 20%
python speeeeed.py track.gpx --speedup 20

# Target a 7:30 min/mile pace and shift to end now
python speeeeed.py track.gpx --target-pace 7:30 --shift-to-now

# Specify a custom output file
python speeeeed.py track.gpx --speedup 25 --output faster_track.gpx
```
