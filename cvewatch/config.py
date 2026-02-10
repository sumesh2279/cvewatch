"""Configuration loader for cvewatch."""

import os
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def get_config_dir() -> Path:
    """Return the config directory (~/.cvewatch)."""
    config_dir = Path.home() / ".cvewatch"
    config_dir.mkdir(exist_ok=True, mode=0o700)
    return config_dir


def load_nvd_api_key() -> Optional[str]:
    """Load NVD API key from env or config file."""
    # Check environment variable first
    api_key = os.getenv("CVEWATCH_NVD_API_KEY")
    if api_key:
        return api_key
    
    # Check config file if PyYAML is available
    if HAS_YAML:
        config_file = get_config_dir() / "config.yml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        return config.get("nvd_api_key")
            except Exception:
                pass  # Silently ignore config errors
    
    return None
