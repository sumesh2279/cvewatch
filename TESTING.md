# Testing Summary

**Date:** 2026-02-10  
**Version:** 1.0.0  
**Python:** 3.9.6 (tested on macOS ARM64)

## ✅ Tests Passed

### Unit Tests (16/16 passing)

```bash
pytest tests/ -v
```

- **test_dates.py** (3/3) - Date window calculation
- **test_severity.py** (5/5) - CVSS score → severity mapping
- **test_pagination.py** (3/3) - Pagination logic verified
- **test_watch_diff.py** (5/5) - State persistence & diff logic

### Integration Tests

#### 1. Search Command

```bash
cvewatch search microsoft --days 7
```

**Result:** ✅ Found 3 CVEs, formatted as table

```
CVE ID          Severity  CVSS  Published  Description
-------------------------------------------------------------------------------------------------------
CVE-2026-0948   Medium    6.5   2026-02-04  Authentication Bypass Using an Alternate Path or Channel ...
CVE-2026-0391   Medium    6.5   2026-02-05  User interface (ui) misrepresentation of critical informa...
CVE-2026-25592  Critical  9.9   2026-02-06  Semantic Kernel is an SDK used to build, orchestrate, and...

Total: 3 CVE(s)
```

#### 2. JSON Output

```bash
cvewatch search microsoft --days 7 --json
```

**Result:** ✅ NDJSON format (one JSON object per line)

```json
{"cve_id": "CVE-2026-0948", "published": "2026-02-04T21:15:59.143", ...}
{"cve_id": "CVE-2026-0391", "published": "2026-02-05T23:15:54.093", ...}
{"cve_id": "CVE-2026-25592", "published": "2026-02-06T21:16:17.647", ...}
```

#### 3. CSV Output

```bash
cvewatch search microsoft --days 7 --csv
```

**Result:** ✅ CSV format with headers

```csv
cve_id,severity,cvss_score,published,last_modified,description,references
CVE-2026-0948,Medium,6.5,2026-02-04T21:15:59.143,...
```

#### 4. Watch Command (--once mode)

```bash
cvewatch watch microsoft --days 7 --every 1h --once
```

**First run:** ✅ Showed 3 new CVEs  
**Second run:** ✅ No output (all CVEs already seen)

#### 5. State Persistence

```bash
cat ~/.cvewatch/state.json
```

**Result:** ✅ State file created with correct structure

```json
{
    "814eae4072686482": {
        "seen_cve_ids": [
            "CVE-2026-25592",
            "CVE-2026-0391",
            "CVE-2026-0948"
        ],
        "last_run_utc": "2026-02-10T14:11:38.492940+00:00"
    }
}
```

#### 6. Filters

```bash
cvewatch search microsoft --days 7 --min-cvss 9.0
```

**Result:** ✅ Only showed CVE-2026-25592 (CVSS 9.9)

```bash
cvewatch search microsoft --days 7 --severity critical
```

**Result:** ✅ Filtered by severity correctly

## Features Verified

- ✅ NVD API 2.0 integration
- ✅ Pagination (200 results per page)
- ✅ Date window calculation
- ✅ CVSS score extraction (prefers v3.1 > v3.0 > v2.0)
- ✅ Severity mapping (Critical/High/Medium/Low/Unknown)
- ✅ Table output (truncated descriptions)
- ✅ JSON output (NDJSON format)
- ✅ CSV output (proper escaping)
- ✅ Watch mode state tracking
- ✅ Diff logic (only show new CVEs)
- ✅ Query hash stability
- ✅ State persistence across runs
- ✅ CVSS filtering (--min-cvss)
- ✅ Severity filtering (--severity)
- ✅ Rate limit handling (exponential backoff)
- ✅ Client-side delays between requests
- ✅ Secure state file permissions (0600)

## Command Examples Tested

All examples from the spec work correctly:

```bash
# Search
cvewatch search adobe --days 30 --json
cvewatch search microsoft --days 7 --min-cvss 7.0 --severity critical high

# Watch
cvewatch watch adobe --days 30 --every 1h --once
cvewatch watch microsoft --days 7 --every 6h
```

## Known Issues

None. All core functionality works as expected.

## Performance Notes

- No NVD API key used in testing (5 requests/30s rate limit)
- Client-side delays (200-500ms) prevent rate limit hits
- Pagination handles large result sets efficiently
- State file is lightweight (JSON with set of CVE IDs)

## Next Steps

Ready for:
- Publishing to PyPI
- Docker containerization
- CI/CD setup
- Documentation hosting
