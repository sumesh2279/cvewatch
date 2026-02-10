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

### From source

```bash
git clone https://github.com/sumesh2279/cvewatch.git
cd cvewatch
pip install -e .
```

### From PyPI (after publishing)

```bash
pip install cvewatch
```

## Quick Start

### Search for CVEs

```bash
# Basic search
cvewatch search adobe --days 30

# With filters
cvewatch search adobe --days 30 --min-cvss 7.0 --severity critical high

# JSON output
cvewatch search adobe --days 30 --json

# CSV output
cvewatch search adobe --days 30 --csv
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

Human-readable table with truncated descriptions.

```
CVE ID           Severity  CVSS  Published   Description
--------------------------------------------------------------------------------
CVE-2024-12345   Critical  9.8   2024-02-10  Buffer overflow in Adobe Reader...
CVE-2024-12346   High      8.1   2024-02-09  Use-after-free in Adobe Flash...

Total: 2 CVE(s)
```

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
