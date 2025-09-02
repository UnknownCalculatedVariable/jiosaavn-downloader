"""
Utility functions for the JioSaavn downloader.
"""

import re
import subprocess
import json
from typing import Tuple, List, Dict, Any
from pathlib import Path


def sanitize(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip()


def run_stream(cmd) -> Tuple[int, list]:
    """
    Run a subprocess and stream stdout lines back; returns (rc, lines)
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = []
    for line in proc.stdout:
        lines.append(line.rstrip("\n"))
        yield ("line", line.rstrip("\n"))
    rc = proc.wait()
    yield ("rc", rc)


def probe_info(url: str) -> Dict[str, Any]:
    """Get detailed info using yt-dlp"""
    cmd = ["yt-dlp", "--ignore-config", "--dump-single-json", url]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        return json.loads(out)
    except subprocess.CalledProcessError:
        # Try with different extractor options
        cmd = ["yt-dlp", "--ignore-config", "--dump-single-json", "--extractor-args", "jiosaavn:all", url]
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            return json.loads(out)
        except:
            return {}


def pick_artists(meta: dict):
    """Extract artist names from metadata."""
    if meta.get("artist"):
        return [meta["artist"]]
    if meta.get("artists"):
        if isinstance(meta["artists"], list):
            return [a.get("name", a) if isinstance(a, dict) else str(a) for a in meta["artists"]]
        return [str(meta["artists"])]
    if meta.get("creator"):
        return [meta["creator"]]
    return ["Unknown Artist"]


def choose_outputs(entry, base_out_dir: Path, force_album_layout: bool):
    """Determine output directory and filename based on entry metadata."""
    artist_list = pick_artists(entry)
    artist = "; ".join(artist_list) if artist_list else None
    album = entry.get("album") or entry.get("album_name") or entry.get("playlist") or entry.get("series") or "Unknown Album"
    title = entry.get("title") or entry.get("track") or "Unknown Title"
    tracknum = None
    
    if entry.get("track_number"):
        tracknum = str(entry["track_number"])
    elif entry.get("playlist_index"):
        tracknum = str(entry["playlist_index"])
    elif entry.get("playlist_autonumber"):
        tracknum = str(entry["playlist_autonumber"])

    if force_album_layout:
        subdir = base_out_dir / sanitize(album)
    else:
        subdir = base_out_dir / (sanitize(album) if (entry.get("_type") == "playlist" or entry.get("n_entries", 0) > 1) else "")
    subdir.mkdir(parents=True, exist_ok=True)

    if tracknum:
        filename = f"{tracknum.zfill(2)} - {sanitize(title)}"
    else:
        if artist:
            filename = f"{sanitize(artist)} - {sanitize(title)}"
        else:
            filename = sanitize(title)

    return subdir, filename, artist_list, album, title, tracknum