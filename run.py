#!/usr/bin/env python3
"""
Simple runner script for the JioSaavn downloader.
"""

import sys
from rich.console import Console
from src.main import main

if __name__ == "__main__":
    console = Console()
    print("Starting JioSaavn Downloader...")
    main()