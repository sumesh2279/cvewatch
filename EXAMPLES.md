# Real-World Usage Examples

## Cybersecurity Consulting Scenarios

### Scenario 1: Client Tech Stack Monitoring

**Context:** You're advising a client using Microsoft, Adobe, and Oracle products.

```bash
# Monitor critical/high severity CVEs for all three vendors
cvewatch watch "microsoft OR adobe OR oracle" --days 30 --every 6h \
  --severity critical high --min-cvss 7.0
```

**What happens:**
- Runs every 6 hours
- Only shows NEW CVEs (not already seen)
- Filters for high-impact vulnerabilities
- Perfect for daily client briefings

### Scenario 2: Weekly Threat Intel Report

**Context:** You need to generate a weekly CVE summary for your manager.

```bash
# Export last 7 days of critical CVEs to CSV
cvewatch search "windows OR linux OR kubernetes" --days 7 \
  --severity critical --csv > weekly_cves_$(date +%Y-%m-%d).csv
```

**Output:** CSV file ready for Excel/Google Sheets with:
- CVE IDs
- CVSS scores
- Descriptions
- Reference links

### Scenario 3: Emergency Triage

**Context:** Client asks "Are we affected by this new Adobe RCE?"

```bash
# Quick search for Adobe CVEs in last 3 days
cvewatch search adobe --days 3 --min-cvss 7.0 --json | jq .
```

**Why JSON?**
- Pipe to `jq` for filtering
- Parse with scripts
- Feed into SIEM/ticketing systems

### Scenario 4: Automated Slack Notifications

**Context:** You want your team alerted when critical CVEs drop.

```bash
#!/bin/bash
# slack-cve-monitor.sh

OUTPUT=$(cvewatch watch "microsoft OR apache" --days 7 \
  --severity critical --every 1h --once --json)

if [ -n "$OUTPUT" ]; then
  # New CVEs found - send to Slack
  curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"🚨 New Critical CVEs:\n\`\`\`$OUTPUT\`\`\`\"}"
fi
```

**Run via cron:**
```cron
0 */1 * * * /path/to/slack-cve-monitor.sh
```

### Scenario 5: Patch Priority List

**Context:** Generate a prioritized patch list for your team.

```bash
# Get all vulnerabilities for last 30 days, sorted by CVSS
cvewatch search "windows OR linux" --days 30 --json | \
  jq -r 'sort_by(-.cvss_score) | .[] | 
    "\(.cve_id) | CVSS \(.cvss_score) | \(.description[:80])"' | \
  head -20
```

**Output:** Top 20 CVEs by severity for action planning.

## Advanced Filters

### Filter by Multiple Vendors

```bash
cvewatch search "cisco OR juniper OR palo alto" --days 14 --severity high critical
```

### Specific Product Monitoring

```bash
cvewatch watch "apache tomcat" --days 7 --every 6h --min-cvss 5.0
```

### Recent Zero-Days

```bash
cvewatch search "zero-day OR 0day" --days 3 --severity critical
```

## Integration Examples

### 1. Feed into SIEM

```bash
# Continuous feed to Splunk via HEC
while true; do
  cvewatch watch "$KEYWORDS" --days 7 --every 10m --once --json | \
    curl -k https://splunk.company.com:8088/services/collector \
      -H "Authorization: Splunk $SPLUNK_TOKEN" \
      -d @-
done
```

### 2. Daily Email Digest

```bash
#!/bin/bash
# daily-cve-digest.sh

DATE=$(date +%Y-%m-%d)
REPORT="/tmp/cve-report-$DATE.txt"

echo "CVE Report - $DATE" > $REPORT
echo "==================" >> $REPORT
echo "" >> $REPORT

cvewatch search "$CLIENT_TECH_STACK" --days 1 --severity critical high >> $REPORT

mail -s "Daily CVE Digest - $DATE" team@company.com < $REPORT
```

### 3. Jira Ticket Creation

```python
#!/usr/bin/env python3
# create-cve-tickets.py

import json
import subprocess
from jira import JIRA

# Fetch new CVEs
result = subprocess.run(
    ['cvewatch', 'watch', 'microsoft', '--days', '7', '--every', '1h', '--once', '--json'],
    capture_output=True, text=True
)

if not result.stdout.strip():
    exit(0)  # No new CVEs

jira = JIRA('https://jira.company.com', basic_auth=('user', 'token'))

for line in result.stdout.strip().split('\n'):
    cve = json.loads(line)
    
    jira.create_issue(
        project='SEC',
        summary=f"{cve['cve_id']} - {cve['severity']} Severity",
        description=f"CVSS: {cve['cvss_score']}\n\n{cve['description']}\n\nReferences:\n" + 
                    "\n".join(cve['references']),
        issuetype={'name': 'Vulnerability'}
    )
```

### 4. GitHub Security Advisory Sync

```bash
#!/bin/bash
# Sync CVEs to GitHub repo issues

cvewatch watch "nodejs OR react OR express" --days 7 --every 12h --once --json | \
  jq -r '"[\(.cve_id)] \(.severity): \(.description[:100])"' | \
  while read TITLE; do
    gh issue create --title "$TITLE" --label "security,cve" --body "Auto-created from CVE feed"
  done
```

## State Management

### View Current State

```bash
cat ~/.cvewatch/state.json | jq .
```

### Reset Watch State (Start Fresh)

```bash
rm ~/.cvewatch/state.json
# Next watch run will show ALL CVEs as "new"
```

### Monitor Multiple Queries Separately

```bash
# Each combination of query+filters gets its own state key
cvewatch watch "microsoft" --days 7 --every 1h &
cvewatch watch "linux kernel" --days 7 --every 1h &
cvewatch watch "apache" --days 7 --every 1h &
```

Each watch runs independently with its own seen CVEs.

## Performance Tips

### Narrow Your Date Window

```bash
# Instead of --days 365 (slow, lots of results)
cvewatch search adobe --days 30  # Faster, more relevant
```

### Use --min-cvss to Focus

```bash
# Only show actionable vulnerabilities
cvewatch search "$VENDORS" --days 7 --min-cvss 7.0
```

### Batch with --once for Cron Jobs

```bash
# Don't run continuous watch in cron - use --once
*/30 * * * * cvewatch watch "keywords" --days 7 --every 1h --once
```

## Debugging

### Enable Debug Mode

```bash
cvewatch --debug search adobe --days 7
```

Shows:
- HTTP requests to NVD API
- Pagination progress
- Rate limit delays
- State operations

### Check API Rate Limits

```bash
# Without API key: 5 requests per 30s
# With API key: 50 requests per 30s

# Monitor your requests:
cvewatch --debug search adobe --days 90 2>&1 | grep "GET https"
```

## Best Practices

1. **Use watch mode for continuous monitoring** - More efficient than repeated searches
2. **Set API key for production** - Avoid rate limits
3. **Filter aggressively** - Use --min-cvss and --severity to reduce noise
4. **Archive state periodically** - Backup ~/.cvewatch/state.json
5. **Log output** - Redirect to files for audit trails

## Common Workflows

### Morning Briefing

```bash
# What happened overnight?
cvewatch watch "$CLIENT_KEYWORDS" --days 1 --every 8h --once --severity critical high
```

### Client Onboarding

```bash
# Historical view of their tech stack
cvewatch search "$NEW_CLIENT_TECH" --days 90 --csv > client-cve-history.csv
```

### Incident Response

```bash
# Zero-day just announced - check exposure
cvewatch search "CVE-2024-12345" --days 1 --json
```

---

**More examples?** Check the GitHub wiki or open an issue!
