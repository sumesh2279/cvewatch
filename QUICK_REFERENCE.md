# cvewatch Quick Reference Card

## Installation

```bash
cd cvewatch-project
pip install -e .
```

## Basic Commands

### Search (one-time)

```bash
# Basic search
cvewatch search <query> --days <N>

# With filters
cvewatch search <query> --days <N> --min-cvss 7.0 --severity critical high

# Output formats
cvewatch search <query> --days <N> --json   # NDJSON
cvewatch search <query> --days <N> --csv    # CSV
```

### Watch (continuous monitoring)

```bash
# Run once (for testing)
cvewatch watch <query> --days <N> --every <duration> --once

# Continuous (Ctrl+C to stop)
cvewatch watch <query> --days <N> --every <duration>

# With filters
cvewatch watch <query> --days <N> --every <duration> --min-cvss 7.0 --severity critical
```

## Common Patterns

### Monitor Client Tech Stack

```bash
cvewatch watch "microsoft OR adobe OR oracle" --days 30 --every 6h --severity critical high
```

### Weekly Report

```bash
cvewatch search "windows OR linux" --days 7 --csv > report.csv
```

### Emergency Check

```bash
cvewatch search "CVE-2026-12345" --days 1 --json
```

### High-CVSS Only

```bash
cvewatch search <query> --days 30 --min-cvss 9.0
```

## Filters

| Option | Values | Example |
|--------|--------|---------|
| `--days` | Number (1-365) | `--days 30` |
| `--min-cvss` | Float (0.0-10.0) | `--min-cvss 7.0` |
| `--severity` | critical, high, medium, low | `--severity critical high` |
| `--every` | 30m, 1h, 6h, 24h, 1d | `--every 6h` |
| `--json` | Flag | `--json` |
| `--csv` | Flag | `--csv` |
| `--once` | Flag (watch only) | `--once` |
| `--debug` | Flag | `--debug` |

## Output Formats

| Format | Command | Use Case |
|--------|---------|----------|
| **Table** | (default) | Human reading |
| **JSON** | `--json` | Scripts, APIs, jq |
| **CSV** | `--csv` | Excel, Sheets |

## Configuration

### NVD API Key (Optional)

**Environment variable:**
```bash
export CVEWATCH_NVD_API_KEY="your-key-here"
```

**Config file:** `~/.cvewatch/config.yml`
```yaml
nvd_api_key: your-key-here
```

Get a key: https://nvd.nist.gov/developers/request-an-api-key

## State Management

| Action | Command |
|--------|---------|
| View state | `cat ~/.cvewatch/state.json | jq .` |
| Reset state | `rm ~/.cvewatch/state.json` |
| Backup state | `cp ~/.cvewatch/state.json backup.json` |

## Severity Mapping

| CVSS Score | Severity |
|------------|----------|
| 9.0 - 10.0 | Critical |
| 7.0 - 8.9  | High |
| 4.0 - 6.9  | Medium |
| 0.1 - 3.9  | Low |
| No score   | Unknown |

## Integration Examples

### Cron Job (every hour)

```bash
# crontab -e
0 * * * * /path/to/cvewatch watch "keywords" --days 7 --every 1h --once
```

### Slack Notification

```bash
#!/bin/bash
OUTPUT=$(cvewatch watch "$KEYWORDS" --days 7 --every 1h --once --json)
if [ -n "$OUTPUT" ]; then
  curl -X POST $SLACK_WEBHOOK \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"🚨 New CVEs:\\n\`\`\`$OUTPUT\`\`\`\"}"
fi
```

### Python Script

```python
import subprocess
import json

result = subprocess.run(
    ['cvewatch', 'search', 'microsoft', '--days', '7', '--json'],
    capture_output=True, text=True
)

for line in result.stdout.strip().split('\n'):
    if line:
        cve = json.loads(line)
        print(f"Found: {cve['cve_id']} - CVSS {cve['cvss_score']}")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Add to PATH or use full path |
| Rate limited | Set NVD API key or reduce frequency |
| No results | Try broader date range (`--days`) |
| Old Python | Need Python 3.9+ |

## File Locations

| File | Location |
|------|----------|
| Config | `~/.cvewatch/config.yml` |
| State | `~/.cvewatch/state.json` |
| Install | `pip show cvewatch` |

## Testing

```bash
# Run tests
pytest tests/ -v

# Lint code
ruff check cvewatch/

# Build package
python -m build
```

## Help

```bash
cvewatch --help
cvewatch search --help
cvewatch watch --help
```

---

**Quick Tip:** Start with `--once` flag to test watch mode before running continuously!

**Rate Limits:**
- No API key: 5 requests / 30 seconds
- With API key: 50 requests / 30 seconds

**Need more help?** See [README.md](README.md) or [EXAMPLES.md](EXAMPLES.md)
