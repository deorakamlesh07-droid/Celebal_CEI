import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import threading
from typing import Optional

class SummaryCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._cleanup_old_entries()

    def _get_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> Optional[dict]:
        path = self._get_path(key)
        if not path.exists():
            return None
        
        with self.lock:
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("result")
            except Exception:
                return None

    def set(self, key: str, result: dict) -> None:
        path = self._get_path(key)
        with self.lock:
            try:
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                }
                with path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                pass # Fail silently on cache write error

    def has(self, key: str) -> bool:
        return self._get_path(key).exists()
        
    def _cleanup_old_entries(self):
        """Remove cache entries older than 7 days"""
        try:
            now = datetime.now()
            for path in self.cache_dir.glob("*.json"):
                if not path.is_file():
                    continue
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if now - mtime > timedelta(days=7):
                    try:
                        path.unlink()
                    except OSError:
                        pass
        except Exception:
            pass

def generate_cache_key(text: str, level: str, scope: str) -> str:
    # Hash the first 1000 characters and the length to handle large documents efficiently
    content_repr = f"{text[:1000]}_{len(text)}_{level}_{scope}"
    return hashlib.md5(content_repr.encode("utf-8")).hexdigest()
