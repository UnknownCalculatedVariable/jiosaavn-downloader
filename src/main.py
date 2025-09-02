"""
Main entry point for the JioSaavn downloader.
"""

import argparse
from pathlib import Path
from .downloader import process_url


def main():
    """Main entry point for the JioSaavn downloader."""
    parser = argparse.ArgumentParser(description="Download JioSaavn tracks/albums with embedded cover art")
    parser.add_argument("url", help="JioSaavn song or album URL")
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--album", action="store_true", help="Force album-style folder layout")
    parser.add_argument("--mp3-320", action="store_true", help="Output MP3 ~320 kbps instead of FLAC")
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    to_mp3_320 = args.mp3_320
    to_flac = not to_mp3_320

    try:
        process_url(args.url, out_dir, to_flac, to_mp3_320, args.album)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
