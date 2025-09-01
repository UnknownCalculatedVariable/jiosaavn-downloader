#!/usr/bin/env python3
"""
JioSaavn Downloader - Downloads songs from JioSaavn links with customizable format and bitrate
"""

import argparse
from rich.console import Console

from jiosaavn_downloader.downloader import JioSaavnDownloader


def main():
    parser = argparse.ArgumentParser(description='Download songs from JioSaavn with customizable format and bitrate')
    parser.add_argument('url', help='JioSaavn song URL')
    parser.add_argument('-o', '--output', default='.', help='Output directory (default: current directory)')
    parser.add_argument('-f', '--format', default='flac', choices=['mp3', 'flac', 'm4a', 'opus', 'wav'], 
                       help='Audio format (default: flac)')
    parser.add_argument('-b', '--bitrate', default='320', choices=['128', '192', '256', '320'],
                       help='Audio bitrate in kbps (default: 320, ignored for lossless formats)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('https://www.jiosaavn.com/song/'):
        console = Console()
        console.print("[red]Error: Please provide a valid JioSaavn song URL[/red]")
        return
    
    # Adjust bitrate for lossless formats
    actual_bitrate = args.bitrate
    if args.format in ['flac', 'wav']:
        actual_bitrate = '0'  # Best quality for lossless formats
        console = Console()
        console.print(f"[yellow]Note: Bitrate option ignored for {args.format.upper()} format (using best quality)[/yellow]")
    
    downloader = JioSaavnDownloader()
    success = downloader.process_url(args.url, args.output, args.format, actual_bitrate)
    
    if success:
        downloader.console.print("[bold green]Download completed successfully![/bold green]")
        return 0  # Success
    else:
        downloader.console.print("[bold red]Download failed![/bold red]")
        return 1  # Error
        return 1  # Return error code

    return 0  # Return success code


if __name__ == "__main__":
    exit(main())