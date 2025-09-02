"""
Download logic and progress handling for the JioSaavn downloader.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn

from .utils import probe_info, choose_outputs
from .metadata import tag_flac, tag_mp3


progress_line_re = re.compile(
    r"^\[download\]\s+(\d{1,3}\.\d)%\s+of\s+([\d\.]+[KMG]iB)\s+at\s+([\d\.]+[KMG]iB/s)\s+ETA\s+([\d:]+)"
)


def download_with_progress(entry_url: str, outtmpl: str, to_flac: bool, to_mp3_320: bool, 
                           track_task=None, progress: Optional[Progress]=None) -> int:
    """Download a track with progress bar."""
    base = [
        "yt-dlp",
        "--ignore-config",
        "--no-part",
        "--prefer-ffmpeg",
        "--embed-thumbnail",
        "--add-metadata",
        "--no-playlist",
        "--extractor-args", "jiosaavn:all",
    ]
    post = []
    if to_mp3_320:
        post = ["-x", "--audio-format", "mp3", "--audio-quality", "320K"]
    elif to_flac:
        post = ["-x", "--audio-format", "flac"]

    cmd = base + post + ["-o", outtmpl, entry_url]

    # Stream output and update Rich bars
    last_percent = 0.0
    for kind, payload in run_stream(cmd):
        if kind == "line":
            line = payload
            if progress and track_task is not None:
                m = progress_line_re.match(line.strip())
                if m:
                    pct = float(m.group(1))
                    delta = max(0.0, pct - last_percent)
                    last_percent = pct
                    progress.update(track_task, completed=pct, total=100)
        elif kind == "rc":
            rc = payload
            return rc
    return 1


def run_stream(cmd):
    """Helper function to stream subprocess output."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout:
        yield ("line", line.rstrip("\n"))
    rc = proc.wait()
    yield ("rc", rc)


def process_url(url: str, out_dir: Path, to_flac: bool, to_mp3_320: bool, album_layout: bool):
    """Process a URL and download tracks."""
    print(f"Processing: {url}")
    
    # First get info to determine if it's a playlist
    info = probe_info(url)
    if not info:
        print("Error: Could not extract information from the URL")
        return

    is_playlist = info.get("_type") == "playlist" or info.get("n_entries", 0) > 1
    
    if is_playlist:
        print(f"Detected playlist with {info.get('n_entries', 'unknown')} entries")
        entries = info.get("entries", [])
        if not entries:
            print("No entries found in playlist")
            return
    else:
        entries = [info]

    with Progress(
        TextColumn("[bold]Downloading[/bold]"),
        BarColumn(),
        TextColumn("{task.percentage:>5.1f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    ) as prog:

        album_task = None
        if is_playlist:
            album_task = prog.add_task("Album", total=len(entries))

        for idx, entry in enumerate(entries, start=1):
            if not entry:
                if album_task is not None:
                    prog.advance(album_task, 1)
                continue

            # Get the actual download URL
            track_url = entry.get("webpage_url") or entry.get("url") or url
            if not track_url:
                print(f"Skipping entry {idx}: No URL found")
                continue

            subdir, filename, artists, album, title, tracknum = choose_outputs(entry, out_dir, album_layout or is_playlist)
            outtmpl = str((subdir / f"{filename}.%(ext)s").as_posix())

            # Per-track task
            track_label = f"{(tracknum or str(idx)).zfill(2)} {title[:30]}{'...' if len(title) > 30 else ''}"
            track_task = prog.add_task(track_label, total=100)

            print(f"Downloading: {title}")
            rc = download_with_progress(
                entry_url=track_url,
                outtmpl=outtmpl,
                to_flac=to_flac,
                to_mp3_320=to_mp3_320,
                track_task=track_task,
                progress=prog,
            )

            # Finalize track task
            prog.update(track_task, completed=100)
            prog.remove_task(track_task)

            # Tag the file
            ext = "mp3" if to_mp3_320 else "flac"
            final_path = subdir / f"{filename}.{ext}"
            
            if final_path.exists():
                if ext == "flac":
                    tag_flac(final_path, entry)
                elif ext == "mp3":
                    tag_mp3(final_path, entry)
                print(f"Downloaded: {final_path.name}")
            else:
                print(f"Warning: Expected file not found: {final_path}")

            if album_task is not None:
                prog.advance(album_task, 1)