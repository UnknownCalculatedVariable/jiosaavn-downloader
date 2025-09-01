import os
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB


def add_metadata_to_file(file_path, song_info, cover_art_path=None, console=None):
    """Add metadata to audio file using mutagen with progress indication"""
    try:
        if console:
            with console.status("[bold green]Adding metadata...") as status:
                _add_metadata(file_path, song_info, cover_art_path, console)
        else:
            _add_metadata(file_path, song_info, cover_art_path, console)
            
    except Exception as e:
        if console:
            console.print(f"[red]Error adding metadata: {e}[/red]")


def _add_metadata(file_path, song_info, cover_art_path=None, console=None):
    """Internal function to add metadata to audio file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.flac':
        audio = FLAC(file_path)
        
        # Clear existing metadata
        audio.delete()
        
        # Add basic metadata
        audio['title'] = song_info['title']
        audio['artist'] = song_info['artist']
        audio['album'] = song_info['album']
        
        # Add cover art if available
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    image_data = img.read()
                
                picture = Picture()
                picture.data = image_data
                picture.type = 3  # Front cover
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                
                audio.add_picture(picture)
            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding cover art: {e}[/yellow]")
        
        audio.save()
        
    elif file_ext == '.mp3':
        # For MP3 files, use ID3 tags
        audio = MP3(file_path, ID3=ID3)
        
        # Ensure ID3 tag exists
        try:
            audio.add_tags()
        except:
            pass
        
        # Add basic metadata
        audio.tags.add(TIT2(encoding=3, text=song_info['title']))
        audio.tags.add(TPE1(encoding=3, text=song_info['artist']))
        audio.tags.add(TALB(encoding=3, text=song_info['album']))
        
        # Add cover art if available
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    image_data = img.read()
                
                audio.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime='image/jpeg',
                        type=3,  # Front cover
                        desc='Cover',
                        data=image_data
                    )
                )
            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding cover art: {e}[/yellow]")
        
        audio.save()
    
    if console:
        console.print(f"[green]Metadata added to:[/green] {os.path.basename(file_path)}")