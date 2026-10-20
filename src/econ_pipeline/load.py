"""Stage 1 (load): download raw World Bank indicator data.

Raw files are saved exactly as received, made read-only, and recorded in a
manifest so we always know where each file came from and when.
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://api.worldbank.org/v2/en/indicator/{code}?downloadformat=csv"

# name -> World Bank indicator code. Add new indicators here to scale the project.
INDICATORS = {
    "inflation": "FP.CPI.TOTL.ZG",
    "exchange_rate": "PA.NUS.FCRF",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
}


def _record_provenance(raw_dir: Path, code: str, url: str, source_name: str) -> None:
    """Append where/when a raw file came from to data/raw/MANIFEST.json."""
    manifest_path = raw_dir / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest[code] = {
        "file": f"{code}.csv",
        "source_url": url,
        "source_file_in_zip": source_name,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def download_indicator(code: str, raw_dir: str | Path, force: bool = False) -> Path:
    """Download one indicator's raw CSV into raw_dir and return its path.

    If the file already exists it is left alone, unless force=True.
    The file is saved unmodified and set to read-only.
    """
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / f"{code}.csv"

    if target.exists() and not force:
        return target

    url = BASE_URL.format(code=code)
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        data_files = [n for n in archive.namelist() if n.startswith("API_")]
        if len(data_files) != 1:
            raise ValueError(f"Expected one data file in zip, found: {archive.namelist()}")
        source_name = data_files[0]
        if target.exists():
            target.chmod(0o644)  # allow overwrite when force=True
        target.write_bytes(archive.read(source_name))

    target.chmod(0o444)  # read-only: raw data is never edited
    _record_provenance(raw_dir, code, url, source_name)
    return target
