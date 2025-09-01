# JioSaavn Downloader

A Python tool to download songs from JioSaavn with customizable format and bitrate. This tool extracts metadata from JioSaavn URLs, searches for the song on YouTube using yt-dlp, downloads it in your preferred format, and adds the original metadata including cover art.

## Features

- Download songs from JioSaavn URLs
- Multiple audio formats supported: MP3, FLAC, M4A, OPUS, WAV
- Customizable bitrate for lossy formats (128k, 192k, 256k, 320k)
- Automatic metadata extraction from JioSaavn (title, artist, album)
- Cover art embedding
- Progress bars for downloads
- Rich terminal interface

## Requirements

- Python 3.6+
- yt-dlp
- ffmpeg

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/jiosaavn-downloader.git
   cd jiosaavn-downloader
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install yt-dlp:
   ```bash
   # Using pip
   pip install yt-dlp
   
   # Or using your system package manager
   # Ubuntu/Debian:
   sudo apt install yt-dlp
   
   # macOS:
   brew install yt-dlp
   ```

4. Install ffmpeg:
   ```bash
   # Ubuntu/Debian:
   sudo apt install ffmpeg
   
   # macOS:
   brew install ffmpeg
   
   # Windows:
   # Download from https://ffmpeg.org/download.html
   ```

## Usage

```bash
python main.py [JIO_SAAVN_URL] [OPTIONS]
```

### Options

- `-o, --output DIR` - Output directory (default: current directory)
- `-f, --format FORMAT` - Audio format (mp3, flac, m4a, opus, wav) (default: flac)
- `-b, --bitrate BITRATE` - Audio bitrate (128, 192, 256, 320) (default: 320)

### Examples

Download a song in FLAC format (lossless):
```bash
python main.py https://www.jiosaavn.com/song/some-song/long-url-here
```

Download a song in MP3 format at 320kbps:
```bash
python main.py https://www.jiosaavn.com/song/some-song/long-url-here -f mp3 -b 320
```

Download a song to a specific directory:
```bash
python main.py https://www.jiosaavn.com/song/some-song/long-url-here -o ~/Music
```

## How It Works

1. The tool extracts metadata (title, artist, album, cover art) from the JioSaavn URL
2. It uses yt-dlp to search YouTube for the song using the extracted metadata
3. The song is downloaded in the specified format and bitrate
4. Metadata and cover art are embedded into the downloaded file using mutagen

## Project Structure

```
jiosaavn-downloader/
├── jiosaavn_downloader/
│   ├── __init__.py
│   ├── downloader.py
│   ├── metadata.py
│   ├── utils.py
│   └── exceptions.py
├── main.py
├── requirements.txt
├── config.json
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the terms of service of JioSaavn and YouTube. Only download content that you have the right to access and use.