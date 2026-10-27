"""Put the site-taste scripts on the import path for the tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "site-taste" / "scripts"
sys.path.insert(0, str(SCRIPTS))
