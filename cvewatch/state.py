"""State management for watch mode."""

import json
import hashlib
from pathlib import Path
from typing import Set, Optional, Dict, Any, List
from datetime import datetime, timezone

from .config import get_config_dir


def compute_query_hash(query: str, days: int, min_cvss: Optional[float], severities: Optional[List[str]]) -> str:
    """Compute stable hash for query + filters."""
    parts = [
        query,
        str(days),
        str(min_cvss) if min_cvss is not None else "",
        ",".join(sorted(severities)) if severities else ""
    ]
    data = "|".join(parts).encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


class WatchState:
    """Manage watch state persistence."""
    
    def __init__(self):
        self.state_file = get_config_dir() / "state.json"
        self.data: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Load state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.data = json.load(f)
            except Exception:
                # If state is corrupted, start fresh
                self.data = {}
    
    def _save(self):
        """Save state to disk with secure permissions."""
        self.state_file.parent.mkdir(exist_ok=True, mode=0o700)
        
        with open(self.state_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        # Set restrictive permissions (user-only)
        try:
            self.state_file.chmod(0o600)
        except Exception:
            pass  # Best effort on Windows
    
    def get_seen_cves(self, query_hash: str) -> Set[str]:
        """Get set of seen CVE IDs for a query."""
        if query_hash in self.data:
            return set(self.data[query_hash].get("seen_cve_ids", []))
        return set()
    
    def update_seen_cves(self, query_hash: str, cve_ids: Set[str]):
        """Update seen CVE IDs for a query."""
        if query_hash not in self.data:
            self.data[query_hash] = {}
        
        self.data[query_hash]["seen_cve_ids"] = list(cve_ids)
        self.data[query_hash]["last_run_utc"] = datetime.now(timezone.utc).isoformat()
        
        self._save()
    
    def get_last_run(self, query_hash: str) -> Optional[str]:
        """Get last run timestamp for a query."""
        if query_hash in self.data:
            return self.data[query_hash].get("last_run_utc")
        return None
