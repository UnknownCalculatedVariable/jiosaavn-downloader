import re
import json
import os
from urllib.parse import urlparse, unquote

from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    DownloadColumn, 
    TransferSpeedColumn,
    TimeRemainingColumn
)


def extract_song_info_from_url(session, url, console):
    """Extract song information from JioSaavn URL"""
    try:
        with console.status("[bold green]Extracting song information...") as status:
            # Get the HTML content
            response = session.get(url)
            response.raise_for_status()
            
            # Look for JSON data in the HTML
            html_content = response.text
            
            # Try to find song data in script tags
            pattern = r'<script type="application/ld\+json">(.*?)</script>'
            matches = re.findall(pattern, html_content, re.DOTALL)
            
            song_data = None
            for match in matches:
                try:
                    data = json.loads(match.strip())
                    if data.get('@type') == 'MusicRecording':
                        song_data = data
                        break
                except json.JSONDecodeError:
                    continue
            
            if not song_data:
                # Alternative method: look for window.__INITIAL_DATA__
                pattern = r'window\.__INITIAL_DATA__\s*=\s*({.*?});'
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        # Navigate through the complex JSON structure
                        # Try different possible paths in the complex JSON structure
                        if 'entities' in data and 'songs' in data['entities']:
                            songs = data['entities']['songs']
                            if songs:
                                first_song = list(songs.values())[0]
                                song_data = {
                                    'name': first_song.get('title', 'Unknown Title'),
                                    'byArtist': first_song.get('primary_artists', 'Unknown Artist'),
                                    'inAlbum': first_song.get('album', 'Unknown Album'),
                                    'duration': first_song.get('duration', ''),
                            'image_url': first_song.get('image', [{'url': ''}])[0].get('url', '') if isinstance(first_song.get('image'), list) else first_song.get('image', '')
                                }
                    except json.JSONDecodeError:
                        pass
            
            if song_data:
                return {
                    'title': song_data.get('name', 'Unknown Title'),
                    'artist': song_data.get('byArtist', {}).get('name', 'Unknown Artist') 
                            if isinstance(song_data.get('byArtist'), dict) 
                            else song_data.get('byArtist', 'Unknown Artist'),
                    'album': song_data.get('inAlbum', {}).get('name', 'Unknown Album') 
                           if isinstance(song_data.get('inAlbum'), dict)
                           else song_data.get('inAlbum', 'Unknown Album'),
                    'duration': song_data.get('duration', ''),
                    'image_url': song_data.get('image', [{'url': ''}])[0].get('url', '') if isinstance(song_data.get('image'), list) else song_data.get('image', '')
                }
            
            # Fallback: extract from URL and HTML title
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            song_name = unquote(path_parts[-1]).replace('-', ' ').title()
            
            title_match = re.search(r'<title>(.*?)</title>', html_content)
            if title_match:
                title = title_match.group(1).split(' - ')[0]
                return {
                    'title': title,
                    'artist': 'Unknown Artist',
                    'album': 'Unknown Album',
                    'duration': '',
                    'image_url': ''
                }
            
            return {
                'title': song_name,
                'artist': 'Unknown Artist',
                'album': 'Unknown Album',
                'duration': '',
                'image_url': ''
            }
            
    except Exception as e:
        console.print(f"[red]Error extracting song info: {e}[/red]")
        return None


def download_cover_art(session, url, filename, console):
    """Download cover art image with progress bar"""
    try:
        if not url:
            return None
            
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filename, 'wb') as f:
            with Progress(
                TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
                console=console
            ) as progress:
                download_task = progress.add_task(
                    "download", 
                    filename="Cover Art",
                    total=total_size
                )
                
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    progress.update(download_task, advance=len(data))
        
        return filename
    except Exception as e:
        console.print(f"[red]Error downloading cover art: {e}[/red]")
        return None