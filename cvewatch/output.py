"""Output formatters for CVE records."""

import json
import csv
import sys
from typing import List, Dict, Any, TextIO


def format_table(records: List[Dict[str, Any]], output: TextIO = sys.stdout):
    """Format records as a human-readable table."""
    if not records:
        output.write("No CVEs found.\n")
        return
    
    # Calculate column widths
    col_widths = {
        "cve_id": max(len("CVE ID"), max(len(r["cve_id"]) for r in records)),
        "severity": max(len("Severity"), max(len(r["severity"]) for r in records)),
        "cvss": len("CVSS"),
        "published": len("Published"),
        "description": 60  # Fixed width for description
    }
    
    # Header
    header = (
        f"{'CVE ID':<{col_widths['cve_id']}}  "
        f"{'Severity':<{col_widths['severity']}}  "
        f"{'CVSS':<{col_widths['cvss']}}  "
        f"{'Published':<{col_widths['published']}}  "
        f"{'Description':<{col_widths['description']}}"
    )
    output.write(header + "\n")
    output.write("-" * len(header) + "\n")
    
    # Rows
    for record in records:
        cvss_str = f"{record['cvss_score']:.1f}" if record['cvss_score'] is not None else "N/A"
        published_date = record['published'][:10] if record['published'] else "N/A"
        
        # Truncate description
        desc = record['description']
        if len(desc) > col_widths['description']:
            desc = desc[:col_widths['description']-3] + "..."
        
        row = (
            f"{record['cve_id']:<{col_widths['cve_id']}}  "
            f"{record['severity']:<{col_widths['severity']}}  "
            f"{cvss_str:<{col_widths['cvss']}}  "
            f"{published_date:<{col_widths['published']}}  "
            f"{desc}"
        )
        output.write(row + "\n")
    
    output.write(f"\nTotal: {len(records)} CVE(s)\n")


def format_ndjson(records: List[Dict[str, Any]], output: TextIO = sys.stdout):
    """Format records as NDJSON (one JSON object per line)."""
    for record in records:
        output.write(json.dumps(record) + "\n")


def format_csv_output(records: List[Dict[str, Any]], output: TextIO = sys.stdout):
    """Format records as CSV."""
    if not records:
        return
    
    fieldnames = ["cve_id", "severity", "cvss_score", "published", "last_modified", "description", "references"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for record in records:
        # Join references as semicolon-separated string
        row = record.copy()
        row["references"] = "; ".join(record["references"])
        writer.writerow(row)


def write_output(records: List[Dict[str, Any]], format: str = "table", output: TextIO = sys.stdout):
    """Write records in specified format."""
    if format == "json":
        format_ndjson(records, output)
    elif format == "csv":
        format_csv_output(records, output)
    else:
        format_table(records, output)
