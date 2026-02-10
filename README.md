# cvewatch

Cross-platform CLI tool for monitoring and searching the NVD CVE database. Works with Python 3.9+.

## Features

- **Search** - One-time CVE queries with flexible filters
- **Watch** - Continuous monitoring with diff tracking (only shows new CVEs)
- **Multiple output formats** - Table, JSON (NDJSON), CSV
- **Filters** - By CVSS score, severity, publication date
- **Rate limiting** - Smart backoff and retry logic for NVD API
- **State tracking** - Remembers seen CVEs per query to avoid duplicates

## Installation

### Recommended: Using pipx (easiest)

`pipx` installs CLI tools in isolated environments and makes them available globally. Best for macOS and modern Linux systems.

```bash
# Install pipx first (if not already installed)
brew install pipx  # macOS
# or: apt install pipx  # Debian/Ubuntu

# Install cvewatch directly from GitHub
pipx install git+https://github.com/sumesh2279/cvewatch.git
```

### From source (for development)

```bash
git clone https://github.com/sumesh2279/cvewatch.git
cd cvewatch
pipx install .
```

Or if you prefer using pip with a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### From PyPI (after publishing)

```bash
pipx install cvewatch
```

## Quick Start

### Search for CVEs

```bash
# Basic search
cvewatch search adobe --days 30

# With filters
cvewatch search adobe --days 30 --min-cvss 7.0 --severity critical high

# Show full descriptions and all references
cvewatch search adobe --days 30 --full

# JSON output
cvewatch search adobe --days 30 --json

# CSV output
cvewatch search adobe --days 30 --csv
```

### Show details for a specific CVE

```bash
# View full details for a single CVE
cvewatch show CVE-2025-15556
```

### Watch for new CVEs

```bash
# Run once and show only new CVEs
cvewatch watch adobe --days 30 --every 1h --once

# Continuous monitoring (press Ctrl+C to stop)
cvewatch watch adobe --days 30 --every 6h

# With filters
cvewatch watch adobe --days 30 --every 1h --min-cvss 7.0 --severity critical high
```

## Commands

### `cvewatch search`

Run a one-time CVE query.

**Usage:**
```bash
cvewatch search <query> --days <N> [options]
```

**Options:**
- `--days <N>` - Days to look back (required)
- `--min-cvss <score>` - Minimum CVSS score (e.g., 7.0)
- `--severity <levels>` - Filter by severity (critical, high, medium, low)
- `--full` - Show full descriptions and all references (table mode only)
- `--json` - Output as NDJSON (one JSON object per line)
- `--csv` - Output as CSV
- `--debug` - Enable debug logging

**Examples:**
```bash
# Search for Adobe CVEs in the last 30 days
cvewatch search adobe --days 30

# Search for critical/high severity CVEs
cvewatch search microsoft --days 7 --severity critical high

# Search with CVSS threshold
cvewatch search linux --days 90 --min-cvss 9.0
```

### `cvewatch watch`

Monitor for new CVEs with diff tracking.

**Usage:**
```bash
cvewatch watch <query> --days <N> --every <duration> [options]
```

**Options:**
- `--days <N>` - Days to look back (required)
- `--every <duration>` - Check interval (required): `30m`, `1h`, `6h`, `24h`, `1d`
- `--min-cvss <score>` - Minimum CVSS score
- `--severity <levels>` - Filter by severity
- `--full` - Show full descriptions and all references (table mode only)
- `--json` - Output as NDJSON
- `--once` - Run one watch cycle and exit
- `--debug` - Enable debug logging

**Examples:**
```bash
# Run once to test
cvewatch watch adobe --days 30 --every 1h --once

# Monitor continuously every 6 hours
cvewatch watch adobe --days 30 --every 6h

# Monitor with filters
cvewatch watch microsoft --days 7 --every 1h --min-cvss 7.0 --severity critical high
```

### `cvewatch show`

Display full details for a specific CVE.

**Usage:**
```bash
cvewatch show <CVE-ID>
```

**Description:**
Shows complete information for a single CVE including:
- Full description (not truncated)
- All references with clickable links
- CVSS score and severity
- Published and last modified dates
- Direct NVD link

**Examples:**
```bash
# Show details for a specific CVE
cvewatch show CVE-2025-15556

# Show details for any CVE
cvewatch show CVE-2024-12345
```

## Configuration

### NVD API Key (Optional)

To avoid rate limiting, you can provide an NVD API key:

**Option 1: Environment variable**
```bash
export CVEWATCH_NVD_API_KEY="your-api-key-here"
```

**Option 2: Config file**

Create `~/.cvewatch/config.yml`:
```yaml
nvd_api_key: your-api-key-here
```

Get a free API key at: https://nvd.nist.gov/developers/request-an-api-key

### State File

Watch mode stores seen CVE IDs in `~/.cvewatch/state.json`. This file is automatically created and managed.

## Output Formats

### Table (default)

Human-readable table with truncated descriptions and clickable NVD links.

```
CVE ID           Severity  CVSS  Published   Description
----------------------------------------------------------------------------------------------------
CVE-2024-12345   Critical  9.8   2024-02-10  Buffer overflow in Adobe Reader...
  → https://nvd.nist.gov/vuln/detail/CVE-2024-12345

CVE-2024-12346   High      8.1   2024-02-09  Use-after-free in Adobe Flash...
  → https://nvd.nist.gov/vuln/detail/CVE-2024-12346

Total: 2 CVE(s)
```

Use `--full` to show complete descriptions and all reference links.

### JSON (NDJSON)

One JSON object per line (easy for parsing/streaming).

```json
{"cve_id":"CVE-2024-12345","published":"2024-02-10T12:00:00.000Z",...}
{"cve_id":"CVE-2024-12346","published":"2024-02-09T08:30:00.000Z",...}
```

### CSV

Standard CSV with headers.

```csv
cve_id,severity,cvss_score,published,last_modified,description,references
CVE-2024-12345,Critical,9.8,2024-02-10T12:00:00.000Z,...
```

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run linter
make lint
```

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
cvewatch/
├── cvewatch/
│   ├── __init__.py       # Package init
│   ├── cli.py            # CLI entry point
│   ├── config.py         # Config loader (env + YAML)
│   ├── nvd.py            # NVD API client
│   ├── normalize.py      # CVE normalization
│   ├── output.py         # Output formatters
│   ├── state.py          # State management for watch
│   └── version.py        # Version string
├── tests/
│   ├── test_dates.py     # Date window tests
│   ├── test_severity.py  # Severity mapping tests
│   ├── test_pagination.py # Pagination tests
│   └── test_watch_diff.py # Watch diff logic tests
├── pyproject.toml        # Project metadata + deps
├── Makefile              # Build/test/lint targets
└── README.md             # This file
```

## Rate Limiting

The NVD API has rate limits:
- **Without API key**: 5 requests per 30 seconds
- **With API key**: 50 requests per 30 seconds

cvewatch handles rate limits automatically:
- Exponential backoff with jitter on HTTP 429/503
- Client-side delays between page fetches (200-500ms)
- Clear error messages on persistent failures

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

## Support

- **Issues**: https://github.com/sumesh2279/cvewatch/issues
- **Documentation**: https://github.com/sumesh2279/cvewatch
