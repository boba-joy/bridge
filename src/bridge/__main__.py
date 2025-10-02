"""
Allow running bridge as a module: python -m bridge
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())