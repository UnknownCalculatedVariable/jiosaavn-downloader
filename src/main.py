"""
Main entry point for the JioSaavn downloader.
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.traceback import install

from .downloader import process_url

# Install rich traceback handler for better error visualization
install()
console = Console()


def main():
    """Main entry point for the JioSaavn downloader."""
    parser = argparse.ArgumentParser(description="Download JioSaavn tracks/albums with embedded cover art")
    parser.add_argument("url", help="JioSaavn song or album URL")
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--album", action="store_true", help="Force album-style folder layout")
    parser.add_argument("--mp3-320", action="store_true", help="Output MP3 ~320 kbps instead of FLAC")
    args = parser.parse_args()

    # Check if help was requested
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        return

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    to_mp3_320 = args.mp3_320
    to_flac = not to_mp3_320

    try:
        process_url(args.url, out_dir, to_flac, to_mp3_320, args.album)
    except KeyboardInterrupt:
        console.print("\nDownload interrupted by user")
    except Exception as e:
        console.print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
