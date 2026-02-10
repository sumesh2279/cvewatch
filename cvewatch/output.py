"""Output formatters for CVE records."""

import json
import csv
import sys
from typing import List, Dict, Any, TextIO


def format_table(records: List[Dict[str, Any]], output: TextIO = sys.stdout, full: bool = False):
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
        "description": 60  # Fixed width for description (when not --full)
    }
    
    # Header
    header = (
        f"{'CVE ID':<{col_widths['cve_id']}}  "
        f"{'Severity':<{col_widths['severity']}}  "
        f"{'CVSS':<{col_widths['cvss']}}  "
        f"{'Published':<{col_widths['published']}}  "
        f"Description"
    )
    output.write(header + "\n")
    output.write("-" * 100 + "\n")
    
    # Rows
    for record in records:
        cvss_str = f"{record['cvss_score']:.1f}" if record['cvss_score'] is not None else "N/A"
        published_date = record['published'][:10] if record['published'] else "N/A"
        nvd_url = f"https://nvd.nist.gov/vuln/detail/{record['cve_id']}"
        
        # Truncate description unless --full is set
        desc = record['description']
        if not full and len(desc) > col_widths['description']:
            desc = desc[:col_widths['description']-3] + "..."
        
        row = (
            f"{record['cve_id']:<{col_widths['cve_id']}}  "
            f"{record['severity']:<{col_widths['severity']}}  "
            f"{cvss_str:<{col_widths['cvss']}}  "
            f"{published_date:<{col_widths['published']}}  "
            f"{desc}"
        )
        output.write(row + "\n")
        
        # Always show NVD link
        output.write(f"  → {nvd_url}\n")
        
        # Show references if --full
        if full and record.get('references'):
            output.write(f"  References:\n")
            for ref in record['references']:
                output.write(f"    • {ref}\n")
        
        output.write("\n")
    
    output.write(f"Total: {len(records)} CVE(s)\n")


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


def format_single_cve(record: Dict[str, Any], output: TextIO = sys.stdout):
    """Format a single CVE with full details."""
    output.write(f"\n{'='*80}\n")
    output.write(f"CVE ID: {record['cve_id']}\n")
    output.write(f"{'='*80}\n\n")
    
    # Basic info
    output.write(f"Severity:      {record['severity']}\n")
    cvss_str = f"{record['cvss_score']:.1f}" if record['cvss_score'] is not None else "N/A"
    output.write(f"CVSS Score:    {cvss_str}\n")
    output.write(f"Published:     {record['published']}\n")
    output.write(f"Last Modified: {record['last_modified']}\n")
    output.write(f"NVD Link:      https://nvd.nist.gov/vuln/detail/{record['cve_id']}\n\n")
    
    # Description
    output.write("Description:\n")
    output.write(f"{record['description']}\n\n")
    
    # References
    if record.get('references'):
        output.write(f"References ({len(record['references'])}):\n")
        for ref in record['references']:
            output.write(f"  • {ref}\n")
    
    output.write("\n")


def write_output(records: List[Dict[str, Any]], format: str = "table", output: TextIO = sys.stdout, full: bool = False):
    """Write records in specified format."""
    if format == "json":
        format_ndjson(records, output)
    elif format == "csv":
        format_csv_output(records, output)
    else:
        format_table(records, output, full=full)
