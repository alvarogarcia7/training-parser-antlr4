#!/usr/bin/env python3
"""Download ANTLR 4.9.3 jar if it doesn't exist."""

import sys
from pathlib import Path
from urllib.request import urlretrieve

ANTLR_JAR = "antlr-4.9.3-complete.jar"
ANTLR_URL = "https://www.antlr.org/download/antlr-4.9.3-complete.jar"


def download_antlr() -> int:
    """Download ANTLR jar if it doesn't exist.
    
    Returns:
        0 if successful or already exists, 1 on error
    """
    jar_path = Path(ANTLR_JAR)
    
    if jar_path.exists():
        print(f"ANTLR jar already exists: {ANTLR_JAR}")
        return 0
    
    try:
        print(f"Downloading ANTLR 4.9.3 from {ANTLR_URL}...")
        urlretrieve(ANTLR_URL, ANTLR_JAR)
        print(f"ANTLR jar downloaded: {ANTLR_JAR}")
        return 0
    except Exception as e:
        print(f"Error downloading ANTLR jar: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(download_antlr())
