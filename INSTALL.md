# Installation Guide

## Requirements

- **Python:** 3.9 or higher
- **Platforms:** Linux, macOS, Windows
- **Dependencies:** httpx, PyYAML (auto-installed)

## Quick Install

### From source (recommended for now)

```bash
# Clone the repository
git clone https://github.com/yourusername/cvewatch.git
cd cvewatch

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install without dev dependencies
pip install -e .
```

### From PyPI (after publishing)

```bash
pip install cvewatch
```

## Verify Installation

```bash
cvewatch --version
# Output: cvewatch 1.0.0

cvewatch --help
# Shows command help
```

## Configuration (Optional)

### NVD API Key

Without an API key, you're limited to **5 requests per 30 seconds**. With a key, you get **50 requests per 30 seconds**.

Get a free API key: https://nvd.nist.gov/developers/request-an-api-key

#### Option 1: Environment Variable

```bash
export CVEWATCH_NVD_API_KEY="your-api-key-here"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to persist.

#### Option 2: Config File

Create `~/.cvewatch/config.yml`:

```yaml
nvd_api_key: your-api-key-here
```

The directory and file are created automatically with secure permissions (user-only).

## First Run

Test with a simple search:

```bash
cvewatch search microsoft --days 7
```

Expected output:
```
CVE ID          Severity  CVSS  Published  Description
-------------------------------------------------------------------------------------------------------
CVE-2026-XXXX   Critical  9.8   2026-XX-XX  ...
...

Total: N CVE(s)
```

## Development Setup

For contributing or testing:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter (optional)
ruff check cvewatch/

# Build package
python -m build
```

## Uninstall

```bash
pip uninstall cvewatch
```

To remove all data:

```bash
rm -rf ~/.cvewatch
```

## Troubleshooting

### "Command not found: cvewatch"

The install location may not be in your PATH. Find it:

```bash
python -m pip show cvewatch | grep Location
```

Then check the `bin/` or `Scripts/` subdirectory.

### Rate Limiting

If you see "Rate limited after 5 retries":

1. Get an NVD API key (see Configuration above)
2. Reduce query frequency with watch mode
3. Use narrower date ranges (fewer --days)

### Python Version

Check your Python version:

```bash
python --version
```

If it's below 3.9, upgrade:

- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11` or use pyenv
- **Windows:** Download from https://python.org

## Next Steps

- Read [README.md](README.md) for usage examples
- See [TESTING.md](TESTING.md) for test results
- Check [EXAMPLES.md](EXAMPLES.md) for real-world use cases (TBD)
