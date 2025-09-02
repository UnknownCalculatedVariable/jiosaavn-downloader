"""
Metadata extraction and tagging functionality for the JioSaavn downloader.
"""

from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, TYER, TCON, APIC
from pathlib import Path
from typing import Dict, Any, List
from .utils import pick_artists


def extract_year(meta: dict) -> str:
    """Extract year from metadata."""
    year = None
    for key in ("release_year", "release_date", "upload_date", "timestamp"):
        if meta.get(key):
            year = str(meta[key])[:4]
            break
    return year


def extract_genre(meta: dict) -> str:
    """Extract genre from metadata."""
    if meta.get("genre"):
        if isinstance(meta["genre"], list):
            return "; ".join(meta["genre"])
        else:
            return str(meta["genre"])
    return ""


def tag_flac(path: Path, meta: dict):
    """Tag FLAC files with metadata"""
    try:
        audio = FLAC(str(path))
        title = meta.get("title") or meta.get("track")
        album = meta.get("album") or meta.get("album_name")
        artists = pick_artists(meta)

        if title:
            audio["TITLE"] = title
        if album:
            audio["ALBUM"] = album
        if artists:
            audio["ARTIST"] = "; ".join(artists)
            audio["ALBUMARTIST"] = "; ".join(artists)

        tn = None
        if meta.get("track_number"):
            tn = str(meta["track_number"])
        elif meta.get("playlist_index"):
            tn = str(meta["playlist_index"])
        if tn:
            audio["TRACKNUMBER"] = tn

        year = extract_year(meta)
        if year:
            audio["DATE"] = year

        genre = extract_genre(meta)
        if genre:
            audio["GENRE"] = genre

        audio.save()
    except Exception as e:
        print(f"Warning: Failed to tag FLAC file {path}: {e}")


def tag_mp3(path: Path, meta: dict):
    """Tag MP3 files with metadata"""
    try:
        audio = ID3(str(path))
        
        title = meta.get("title") or meta.get("track")
        album = meta.get("album") or meta.get("album_name")
        artists = pick_artists(meta)

        if title:
            audio.add(TIT2(encoding=3, text=title))
        if album:
            audio.add(TALB(encoding=3, text=album))
        if artists:
            audio.add(TPE1(encoding=3, text="; ".join(artists)))

        tn = None
        if meta.get("track_number"):
            tn = str(meta["track_number"])
        elif meta.get("playlist_index"):
            tn = str(meta["playlist_index"])
        if tn:
            audio.add(TRCK(encoding=3, text=tn))

        year = extract_year(meta)
        if year:
            audio.add(TYER(encoding=3, text=year))

        genre = extract_genre(meta)
        if genre:
            audio.add(TCON(encoding=3, text=genre))

        audio.save()
    except Exception as e:
        print(f"Warning: Failed to tag MP3 file {path}: {e}")