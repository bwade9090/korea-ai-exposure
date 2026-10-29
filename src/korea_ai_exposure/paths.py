"""Repository paths. The package is installed in editable mode, so this file stays in ``src/``."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
MANUAL = DATA / "manual"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
MANIFEST = DATA / "manifest.json"

OUTPUTS = ROOT / "outputs"

ENV_FILE = ROOT / ".env"
SOURCES_REGISTRY = ROOT / "docs" / "DATA_SOURCES.md"
