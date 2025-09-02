# JioSaavn Downloader

A Python tool to download songs and albums from JioSaavn with embedded cover art and metadata.

## Features

- Download individual songs or entire albums/playlists
- Automatically embeds cover art and metadata
- Supports both FLAC and MP3 (320 kbps) formats
- Progress bars for downloads
- Organizes files by album/artist
- Properly tags audio files with metadata

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/jiosaavn-downloader.git
   cd jiosaavn-downloader
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have `ffmpeg` installed on your system:
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from https://ffmpeg.org/download.html

## Usage

### Basic Usage

Download a song or album:
```bash
python run.py "https://www.jiosaavn.com/song/some-song/XXXXXXXXX"
```

### Options

- `--out DIR`: Specify output directory (default: current directory)
- `--album`: Force album-style folder layout
- `--mp3-320`: Download as MP3 at ~320 kbps instead of FLAC

### Examples

Download a song in MP3 format:
```bash
python run.py --mp3-320 "https://www.jiosaavn.com/song/some-song/XXXXXXXXX"
```

Download an album to a specific directory:
```bash
python run.py --out "/path/to/music" "https://www.jiosaavn.com/album/some-album/XXXXXXXXX"
```

## Project Structure

```
jiosaavn-downloader/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── downloader.py        # Download logic and progress handling
│   ├── metadata.py          # Metadata extraction and tagging
│   ├── utils.py             # Utility functions
│   └── models.py            # Data models and types
├── config/
│   └── default_config.json  # Default configuration
├── outputs/                 # Default download directory
├── logs/                    # Log files
├── requirements.txt
├── README.md
└── run.py                  # Simple runner script
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.