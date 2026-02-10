# cvewatch - Project Overview

**Status:** ✅ Complete & Tested  
**Version:** 1.0.0  
**Built:** 2026-02-10  
**For:** Sumesh Adiyapurath

---

## 📋 What Is This?

A cross-platform CLI tool for monitoring and searching the NVD CVE database. Built specifically for cybersecurity professionals who need to:

- Monitor vendor-specific CVEs for clients
- Generate weekly threat intel reports
- Track zero-days and critical vulnerabilities
- Export CVE data to Excel/Jira/SIEM/Slack
- Automate CVE monitoring workflows

## 🎯 Core Features

### 1. Search Mode
One-time CVE queries with flexible filters:

```bash
cvewatch search microsoft --days 30 --min-cvss 7.0 --severity critical high
```

### 2. Watch Mode
Continuous monitoring with diff tracking (only shows NEW CVEs):

```bash
cvewatch watch adobe --days 30 --every 6h
```

### 3. Multiple Output Formats
- **Table** - Human-readable (default)
- **JSON** - NDJSON for scripting/APIs
- **CSV** - Excel/Sheets compatible

### 4. Smart Rate Limiting
- Exponential backoff on HTTP 429/503
- Client-side delays between requests
- Optional NVD API key support

### 5. State Management
- Tracks seen CVEs per query
- Only alerts on NEW vulnerabilities
- Persistent across restarts

## 📁 Project Structure

```
cvewatch-project/
├── cvewatch/              # Main package
│   ├── cli.py            # CLI entry point
│   ├── nvd.py            # NVD API client
│   ├── normalize.py      # CVE data normalization
│   ├── output.py         # Output formatters
│   ├── state.py          # State persistence
│   └── config.py         # Config loader
├── tests/                 # Unit tests (16 passing)
├── pyproject.toml         # Package metadata
├── README.md              # User documentation
├── INSTALL.md             # Installation guide
├── EXAMPLES.md            # Real-world use cases
├── TESTING.md             # Test results
├── BUILD_SUMMARY.md       # Build details
├── Makefile               # Build/test targets
└── LICENSE                # MIT License
```

## 🚀 Quick Start

### Install

```bash
cd cvewatch-project
pip install -e .
```

### Test

```bash
# Search for CVEs
cvewatch search microsoft --days 7

# Watch for new CVEs
cvewatch watch adobe --days 30 --every 1h --once
```

### Run Tests

```bash
pytest tests/ -v
```

## 📊 Test Results

**Unit Tests:** 16/16 passing ✅

- Date calculations
- Severity mapping
- Pagination logic
- State persistence
- Diff tracking

**Integration Tests:** All passing ✅

- Search command
- Watch command
- JSON/CSV output
- Filter combinations
- State tracking

## 🎓 Documentation

| File | Purpose |
|------|---------|
| [README.md](README.md) | User guide & API reference |
| [INSTALL.md](INSTALL.md) | Installation instructions |
| [EXAMPLES.md](EXAMPLES.md) | Real-world use cases |
| [TESTING.md](TESTING.md) | Test results & validation |
| [BUILD_SUMMARY.md](BUILD_SUMMARY.md) | Build details & decisions |

## 💡 Use Cases for You (Sumesh)

### 1. Client Tech Stack Monitoring

Monitor CVEs for specific client technologies:

```bash
cvewatch watch "microsoft OR oracle OR cisco" --days 30 --every 6h \
  --severity critical high --min-cvss 7.0
```

### 2. Weekly Reports

Generate CSV for management:

```bash
cvewatch search "windows OR linux" --days 7 --csv > weekly_report.csv
```

### 3. Emergency Triage

Quick check for new vulnerabilities:

```bash
cvewatch search "CVE-2026-12345" --days 1 --json | jq .
```

### 4. Slack Notifications

Automated alerts (via cron):

```bash
# slack-notify.sh
OUTPUT=$(cvewatch watch "keywords" --days 7 --every 1h --once --json)
if [ -n "$OUTPUT" ]; then
  curl -X POST $SLACK_WEBHOOK -d "{\"text\": \"🚨 New CVEs: $OUTPUT\"}"
fi
```

### 5. Jira Integration

Auto-create security tickets:

```python
for line in cvewatch_output:
    cve = json.loads(line)
    jira.create_issue(project='SEC', summary=f"{cve['cve_id']} - {cve['severity']}")
```

## 🔑 Configuration

### NVD API Key (Optional)

**Without key:** 5 requests/30s  
**With key:** 50 requests/30s

Get a free key: https://nvd.nist.gov/developers/request-an-api-key

**Setup:**

```bash
# Option 1: Environment variable
export CVEWATCH_NVD_API_KEY="your-key"

# Option 2: Config file (~/.cvewatch/config.yml)
nvd_api_key: your-key
```

## 📈 Performance

- **Memory:** ~10MB (grows with result count)
- **API calls:** Efficient pagination (200/page)
- **State file:** Lightweight JSON
- **Rate limits:** Smart backoff prevents bans

## 🔒 Security

- State file: User-only permissions (0600)
- API key: Env var or config file
- No secrets in logs
- HTTPS-only for API calls

## 🛠️ Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
make test
# or
pytest tests/ -v
```

### Lint Code

```bash
make lint
# or
ruff check cvewatch/
```

### Build Package

```bash
make build
# or
python -m build
```

## 📦 Distribution (Next Steps)

Ready for:

1. **PyPI Publishing**
   - `python -m twine upload dist/*`
   - Install via: `pip install cvewatch`

2. **GitHub Release**
   - Tag version: `git tag v1.0.0`
   - Create release with binaries

3. **Homebrew Formula**
   - For macOS users
   - `brew install cvewatch`

4. **Docker Image**
   - For containerized deployments
   - `docker run cvewatch search ...`

## 🔮 Future Features (v2.0)

- SQLite database for historical tracking
- Web dashboard
- Email/Slack/Teams notifications (built-in)
- Custom CVE feeds (not just NVD)
- Export to PDF/Excel
- Multi-tenant support

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Add tests
4. Submit a PR

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🐛 Issues & Support

- **GitHub:** https://github.com/yourusername/cvewatch/issues
- **Docs:** https://github.com/yourusername/cvewatch

---

## ✅ Project Status

**What's Done:**

- [x] Core CLI implementation
- [x] NVD API 2.0 integration
- [x] Search & watch modes
- [x] Table/JSON/CSV outputs
- [x] State persistence & diff tracking
- [x] Rate limiting & retries
- [x] Unit tests (16/16 passing)
- [x] Integration tests (all passing)
- [x] Documentation (README + guides)
- [x] Example use cases

**Ready For:**

- [ ] Publishing to PyPI
- [ ] GitHub repository setup
- [ ] CI/CD pipeline
- [ ] User feedback & iteration

---

**Built with care for the cybersecurity community.** 🦝
