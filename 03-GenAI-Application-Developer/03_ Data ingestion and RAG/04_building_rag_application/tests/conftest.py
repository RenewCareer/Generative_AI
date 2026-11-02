import sys
from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_DIR))
