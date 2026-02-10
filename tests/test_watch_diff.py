"""Test watch mode diff logic."""

import pytest
import tempfile
import json
from pathlib import Path
from cvewatch.state import WatchState, compute_query_hash


def test_query_hash_stability():
    """Test that query hash is stable for same inputs."""
    hash1 = compute_query_hash("adobe", 30, 7.0, ["critical", "high"])
    hash2 = compute_query_hash("adobe", 30, 7.0, ["critical", "high"])
    
    assert hash1 == hash2


def test_query_hash_different():
    """Test that query hash differs for different inputs."""
    hash1 = compute_query_hash("adobe", 30, 7.0, ["critical"])
    hash2 = compute_query_hash("adobe", 30, 7.0, ["high"])
    
    assert hash1 != hash2


def test_state_persistence(tmp_path):
    """Test that state persists across instances."""
    # Create temporary state file
    state_file = tmp_path / "state.json"
    
    # Monkey-patch get_config_dir to use tmp_path
    import cvewatch.state
    original_get_config_dir = cvewatch.state.get_config_dir
    cvewatch.state.get_config_dir = lambda: tmp_path
    
    try:
        # First instance
        state1 = WatchState()
        query_hash = compute_query_hash("test", 30, None, None)
        state1.update_seen_cves(query_hash, {"CVE-2024-0001", "CVE-2024-0002"})
        
        # Second instance (should load from disk)
        state2 = WatchState()
        seen = state2.get_seen_cves(query_hash)
        
        assert "CVE-2024-0001" in seen
        assert "CVE-2024-0002" in seen
        assert len(seen) == 2
    
    finally:
        # Restore original function
        cvewatch.state.get_config_dir = original_get_config_dir


def test_watch_diff_logic():
    """Test that diff logic correctly identifies new CVEs."""
    seen_cves = {"CVE-2024-0001", "CVE-2024-0002"}
    all_cves = {"CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"}
    
    new_cves = all_cves - seen_cves
    
    assert new_cves == {"CVE-2024-0003"}


def test_empty_state():
    """Test behavior with empty state (first run)."""
    import cvewatch.state
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Monkey-patch
        original_get_config_dir = cvewatch.state.get_config_dir
        cvewatch.state.get_config_dir = lambda: tmp_path
        
        try:
            state = WatchState()
            query_hash = "test123"
            
            seen = state.get_seen_cves(query_hash)
            assert len(seen) == 0
            
            last_run = state.get_last_run(query_hash)
            assert last_run is None
        
        finally:
            cvewatch.state.get_config_dir = original_get_config_dir
