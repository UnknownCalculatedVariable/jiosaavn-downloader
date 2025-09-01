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
            pattern = r'<script type="application/ld\\+json">(.*?)</script>'
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
            
            # If we still don't have song data, try alternative method
            if not song_data:
                # Alternative method: look for window.__INITIAL_DATA__
                pattern = r'window\\.__INITIAL_DATA__\\s*=\\s*({.*?});'
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
                                # Try to get image URL from the correct path
                                image_data = first_song.get('image')
                                image_url = ''
                                if isinstance(image_data, list) and len(image_data) > 0:
                                    # Get the highest quality image
                                    image_url = image_data[0].get('url', '') if isinstance(image_data[0], dict) else str(image_data[0])
                                elif isinstance(image_data, str):
                                    image_url = image_data
                                
                                song_data = {
                                    'name': first_song.get('title', 'Unknown Title'),
                                    'byArtist': first_song.get('primary_artists', 'Unknown Artist'),
                                    'inAlbum': first_song.get('album', 'Unknown Album'),
                                    'duration': first_song.get('duration', ''),
                                    'image': image_url
                                }
                    except json.JSONDecodeError:
                        pass
            
            # If we still don't have song data, try another approach
            if not song_data:
                # Look for specific meta tags
                title_match = re.search(r'<meta property="og:title" content="(.*?)"', html_content)
                image_match = re.search(r'<meta property="og:image" content="(.*?)"', html_content)
                
                if title_match:
                    title = title_match.group(1)
                    # Try to extract artist from title (often in format "Song Name - Artist Name")
                    parts = title.split(' - ')
                    song_name = parts[0] if len(parts) > 0 else title
                    artist_name = parts[1] if len(parts) > 1 else 'Unknown Artist'
                    
                    song_data = {
                        'name': song_name,
                        'byArtist': artist_name,
                        'inAlbum': 'Unknown Album',
                        'duration': '',
                        'image': image_match.group(1) if image_match else ''
                    }
            
            if song_data:
                # Extract title
                title = song_data.get('name', 'Unknown Title')
                
                # Extract artist - handle both dict and string formats
                artist = 'Unknown Artist'
                by_artist = song_data.get('byArtist')
                if isinstance(by_artist, dict):
                    artist = by_artist.get('name', 'Unknown Artist')
                elif isinstance(by_artist, str):
                    artist = by_artist
                elif by_artist:
                    artist = str(by_artist)
                    
                # Extract album - handle both dict and string formats
                album = 'Unknown Album'
                in_album = song_data.get('inAlbum')
                if isinstance(in_album, dict):
                    album = in_album.get('name', 'Unknown Album')
                elif isinstance(in_album, str):
                    album = in_album
                elif in_album:
                    album = str(in_album)
                
                # Extract duration
                duration = song_data.get('duration', '')
                
                # Extract image URL - handle both list and string formats
                image_url = ''
                image_data = song_data.get('image')
                if isinstance(image_data, list) and len(image_data) > 0:
                    image_url = image_data[0].get('url', '') if isinstance(image_data[0], dict) else str(image_data[0])
                elif isinstance(image_data, str):
                    image_url = image_data
                elif image_data:
                    image_url = str(image_data)
                
                # Additional fallback for image URL if not found
                if not image_url:
                    # Try to find any image URL in the HTML
                    img_pattern = r'"image":\s*\[?"([^"]*)'
                    img_match = re.search(img_pattern, html_content)
                    if img_match:
                        image_url = img_match.group(1)
                
                return {
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'duration': duration,
                    'image_url': image_url
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
        
        # Verify file was created and has content
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return filename
        else:
            return None
    except Exception as e:
        console.print(f"[red]Error downloading cover art: {e}[/red]")
        return None