import os
import base64
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis


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
        
        # Add basic metadata
        audio['title'] = song_info['title']
        audio['artist'] = song_info['artist']
        audio['album'] = song_info['album']
        
        # Add cover art
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    picture = Picture()
                    picture.data = img.read()
                    picture.type = 3  # Front cover
                    picture.mime = 'image/jpeg'
                    picture.desc = 'Cover'
                    audio.add_picture(picture)
            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding FLAC cover art: {e}[/yellow]")
        
        audio.save()
        
    elif file_ext == '.mp3':
        audio = MP3(file_path, ID3=ID3)
        
        try:
            audio.add_tags()
        except:
            pass
        
        audio.tags.add(TIT2(encoding=3, text=song_info['title']))
        audio.tags.add(TPE1(encoding=3, text=song_info['artist']))
        audio.tags.add(TALB(encoding=3, text=song_info['album']))
        
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=img.read()
                        )
                    )
            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding MP3 cover art: {e}[/yellow]")
        
        audio.save(v2_version=3)
        
    elif file_ext == '.m4a':
        audio = MP4(file_path)
        
        audio['\xa9nam'] = song_info['title']
        audio['\xa9ART'] = song_info['artist']
        audio['\xa9alb'] = song_info['album']
        
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    audio['covr'] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)]
            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding M4A cover art: {e}[/yellow]")
        
        audio.save()
        
    elif file_ext in ['.ogg', '.opus']:
        audio = OggVorbis(file_path)
        
        audio['title'] = song_info['title']
        audio['artist'] = song_info['artist']
        audio['album'] = song_info['album']
        
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, 'rb') as img:
                    image_data = img.read()
                
                picture = Picture()
                picture.data = image_data
                picture.type = 3  # Front cover
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                
                # Encode picture data as base64 and add as a Vorbis comment
                picture_data = picture.write()
                encoded_data = base64.b64encode(picture_data)
                audio['metadata_block_picture'] = [encoded_data.decode('ascii')]

            except Exception as e:
                if console:
                    console.print(f"[yellow]Warning adding Ogg cover art: {e}[/yellow]")
        
        audio.save()

    if console:
        console.print(f"[green]Metadata added to:[/green] {os.path.basename(file_path)}")