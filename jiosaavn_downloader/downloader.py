import os
import re
import json
import subprocess
import requests
from urllib.parse import urlparse, unquote
from mutagen.flac import FLAC, Picture
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

# Rich imports for progress tracking
from rich.console import Console
from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    DownloadColumn, 
    TransferSpeedColumn,
    TimeRemainingColumn
)
from rich.panel import Panel
from rich import print as rprint

from .metadata import add_metadata_to_file
from .utils import extract_song_info_from_url, download_cover_art


class JioSaavnDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.console = Console()

    def download_cover_art(self, url, filename):
        """Download cover art image with progress bar"""
        return download_cover_art(self.session, url, filename, self.console)

    def extract_song_info(self, url):
        """Extract song information from JioSaavn URL"""
        return extract_song_info_from_url(self.session, url, self.console)

    def _extract_from_initial_data(self, data):
        """Extract song info from window.__INITIAL_DATA__"""
        try:
            # Try different possible paths in the complex JSON structure
            if 'entities' in data and 'songs' in data['entities']:
                songs = data['entities']['songs']
                if songs:
                    first_song = list(songs.values())[0]
                    return {
                        'name': first_song.get('title', 'Unknown Title'),
                        'byArtist': first_song.get('primary_artists', 'Unknown Artist'),
                        'inAlbum': first_song.get('album', 'Unknown Album'),
                        'duration': first_song.get('duration', ''),
                        'image': first_song.get('image', '')
                    }
        except:
            pass
        return None

    def search_and_download(self, song_info, output_dir=".", format="flac", bitrate="320"):
        """Search for song on YouTube and download using yt-dlp with progress tracking"""
        if not song_info:
            return None
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create search query
        search_query = f"{song_info['title']} {song_info['artist']} official"
        
        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', song_info['title'])
        safe_artist = re.sub(r'[<>:"/\\|?*]', '', song_info['artist'])
        output_template = os.path.join(output_dir, f"{safe_artist} - {safe_title}.%(ext)s")
        
        # Set audio quality based on format and bitrate
        audio_quality = f"{bitrate}K" if format != "flac" else "0"
        
        # yt-dlp command to search and download best audio
        cmd = [
            'yt-dlp',
            f'ytsearch1:"{search_query}"',
            '--extract-audio',
            '--audio-format', format,
            '--audio-quality', audio_quality,
            '--output', output_template,
            '--add-metadata',
            '--newline',  # Important for progress parsing
            '--no-check-certificate',  # Avoid SSL issues
            '--no-warnings',  # Reduce unnecessary output
            '--quiet',  # Reduce verbosity
            '--no-call-home',  # Disable telemetry
            '--prefer-free-formats',  # Prefer open formats
            '--no-abort-on-error'  # Continue even if some errors occur
        ]
        
        # For audio-only downloads, specify we want the best audio stream only
        if format in ['mp3', 'flac', 'm4a', 'opus', 'wav']:
            cmd.extend(['--format', 'bestaudio/best'])
            # Prevent downloading video files
            cmd.extend(['--restrict-filenames'])  # Use only ASCII characters in filenames
        
        # Add postprocessor args for specific formats
        if format == "mp3":
            cmd.extend(['--postprocessor-args', f'ffmpeg:-b:a {bitrate}k'])
        elif format == "flac":
            cmd.extend(['--postprocessor-args', 'ffmpeg:-c:a flac -compression_level 12'])
        
        try:
            self.console.print(f"[yellow]Searching for:[/yellow] [green]{search_query}[/green]")
            self.console.print(f"[yellow]Format:[/yellow] [green]{format.upper()}[/green] [yellow]Bitrate:[/yellow] [green]{bitrate}k[/green]")
            
            # Start the process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                bufsize=1
            )
            
            # Regex patterns to extract progress information
            download_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%\s+of\s+~?(\d+\.\d+)(\w+)\s+at\s+(\d+\.\d+)(\w+/s)\s+ETA\s+(\d+:\d+)')
            extract_pattern = re.compile(r'\[extractaudio\]\s+Destination:\s+(.+)')
            merge_pattern = re.compile(r'\[Merger\]\s+Merging formats into\s+"(.+)"')
            
            downloaded_file = None
            progress_bar = None
            download_task = None
            
            # Process output in real-time
            for line in process.stdout:
                # Check for download progress
                download_match = download_pattern.search(line)
                if download_match:
                    if progress_bar is None:
                        # Initialize progress bar on first match
                        progress_bar = Progress(
                            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                            BarColumn(bar_width=None),
                            "[progress.percentage]{task.percentage:>3.1f}%",
                            "•",
                            DownloadColumn(),
                            "•",
                            TransferSpeedColumn(),
                            "•",
                            TimeRemainingColumn(),
                            console=self.console
                        )
                        progress_bar.start()
                        download_task = progress_bar.add_task(
                            "download", 
                            filename="Audio",
                            total=100.0
                        )
                    
                    percentage = float(download_match.group(1))
                    progress_bar.update(download_task, completed=percentage)
                
                # Check for file extraction completion
                extract_match = extract_pattern.search(line)
                if extract_match:
                    downloaded_file = extract_match.group(1)
                    if progress_bar:
                        progress_bar.update(download_task, completed=100.0)
                        progress_bar.stop()
                
                # Check for file merging completion (for some formats)
                merge_match = merge_pattern.search(line)
                if merge_match:
                    downloaded_file = merge_match.group(1)
                    if progress_bar:
                        progress_bar.update(download_task, completed=100.0)
                        progress_bar.stop()
            
            # Wait for process to complete
            process.wait()
            
            # Ensure process is completely terminated
            if process.poll() is None:
                process.terminate()
                process.wait()
            
            if progress_bar:
                progress_bar.stop()
            
            if downloaded_file and os.path.exists(downloaded_file):
                return downloaded_file
            else:
                # Try to find the file with the expected extension in the directory
                expected_ext = f".{format}"
                for file in os.listdir(output_dir):
                    if file.endswith(expected_ext):
                        return os.path.join(output_dir, file)
                
                return None
                
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]yt-dlp error: {e}[/red]")
            if hasattr(e, 'stderr') and e.stderr:
                self.console.print(f"[red]stderr: {e.stderr}[/red]")
            return None
        except Exception as e:
            self.console.print(f"[red]Error during download: {e}[/red]")
            return None

    def add_metadata(self, file_path, song_info, cover_art_path=None):
        """Add metadata to audio file using mutagen with progress indication"""
        add_metadata_to_file(file_path, song_info, cover_art_path, self.console)

    def process_url(self, url, output_dir=".", format="flac", bitrate="320"):
        """Process a JioSaavn URL with rich progress indicators"""
        self.console.print(Panel.fit(f"Processing: [link={url}]{url}[/link]"))
        
        # Extract song information
        song_info = self.extract_song_info(url)
        if not song_info or song_info['title'] == 'Unknown Title':
            self.console.print("[red]Failed to extract valid song information[/red]")
            return False
            
        self.console.print(Panel.fit(
            f"[green]Found:[/green] [bold]{song_info['title']}[/bold] by [bold]{song_info['artist']}[/bold]",
            title="Song Information"
        ))
        
        # Download cover art
        cover_path = None
        if song_info.get('image_url'):
            cover_filename = f"cover_{hash(url)}.jpg"
            cover_path = os.path.join(output_dir, cover_filename)
            if not self.download_cover_art(song_info['image_url'], cover_path):
                cover_path = None  # Reset if download failed
        
        # Search and download using yt-dlp
        downloaded_file = self.search_and_download(song_info, output_dir, format, bitrate)
        if not downloaded_file:
            self.console.print("[red]Failed to download song[/red]")
            return False
            
        # Add metadata
        self.add_metadata(downloaded_file, song_info, cover_path)
        
        # Clean up temporary cover art
        if cover_path and os.path.exists(cover_path):
            os.remove(cover_path)
        
        self.console.print(Panel.fit(
            f"[bold green]Successfully downloaded:[/bold green]\n{downloaded_file}",
            title="Download Complete"
        ))
        return True