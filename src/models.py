"""
Data models and types for the JioSaavn downloader.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path


class DownloadOptions:
    """Options for downloading tracks."""
    def __init__(self, to_flac: bool = True, to_mp3_320: bool = False, album_layout: bool = False):
        self.to_flac = to_flac
        self.to_mp3_320 = to_mp3_320
        self.album_layout = album_layout


class TrackInfo:
    """Information about a track."""
    def __init__(self, url: str, title: str, album: str, artists: List[str], 
                 track_number: Optional[str] = None):
        self.url = url
        self.title = title
        self.album = album
        self.artists = artists
        self.track_number = track_number


# Type aliases for better readability
Metadata = Dict[str, Any]
Entry = Dict[str, Any]