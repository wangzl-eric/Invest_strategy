#!/usr/bin/env python3
"""Initialize the quant dataset metadata DB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from quant_data.meta_db import init_meta_db


if __name__ == "__main__":
    print("Initializing quant metadata database...")
    init_meta_db()
    print("Quant metadata database initialized successfully!")

