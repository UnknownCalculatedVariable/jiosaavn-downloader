"""
Custom exceptions for the JioSaavn Downloader
"""


class JioSaavnDownloaderError(Exception):
    """Base exception for JioSaavn Downloader errors"""
    pass


class SongInfoExtractionError(JioSaavnDownloaderError):
    """Raised when song information cannot be extracted from the URL"""
    pass


class DownloadError(JioSaavnDownloaderError):
    """Raised when there is an error downloading the song"""
    pass


class MetadataError(JioSaavnDownloaderError):
    """Raised when there is an error adding metadata to the file"""
    pass


class CoverArtDownloadError(JioSaavnDownloaderError):
    """Raised when there is an error downloading the cover art"""
    pass