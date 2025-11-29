"""Utility functions."""
import hashlib
import json
from pathlib import Path
from typing import Dict, Any


def generate_file_hash(file_path: Path) -> str:
    """Generate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def safe_json_load(file_path: Path) -> Dict[str, Any]:
    """Safely load JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"error": str(e)}


def safe_json_save(data: Dict[str, Any], file_path: Path) -> bool:
    """Safely save data to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

