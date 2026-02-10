"""CLI entry point for cvewatch."""

import argparse
import sys
import time
import re
from typing import Optional, List

from .version import __version__
from .config import load_nvd_api_key
from .nvd import NVDClient
from .normalize import normalize_cve, filter_record
from .output import write_output
from .state import WatchState, compute_query_hash


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds (e.g., '30m', '1h', '24h', '1d')."""
    match = re.match(r'^(\d+)(m|h|d)$', duration_str.lower())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    
    raise ValueError(f"Invalid duration unit: {unit}")


def cmd_search(args):
    """Execute search command."""
    api_key = load_nvd_api_key()
    client = NVDClient(api_key=api_key, debug=args.debug)
    
    records = []
    
    try:
        for vuln_data in client.search_cves(
            query=args.query,
            days=args.days,
            min_cvss=args.min_cvss,
            severities=args.severity
        ):
            record = normalize_cve(vuln_data)
            
            # Apply filters
            if filter_record(record, min_cvss=args.min_cvss, severities=args.severity):
                records.append(record)
        
        # Determine output format
        output_format = "table"
        if args.json:
            output_format = "json"
        elif args.csv:
            output_format = "csv"
        
        write_output(records, format=output_format)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_watch(args):
    """Execute watch command."""
    api_key = load_nvd_api_key()
    client = NVDClient(api_key=api_key, debug=args.debug)
    state = WatchState()
    
    # Compute query hash for state tracking
    query_hash = compute_query_hash(
        query=args.query,
        days=args.days,
        min_cvss=args.min_cvss,
        severities=args.severity
    )
    
    if args.debug:
        print(f"[DEBUG] Query hash: {query_hash}", file=sys.stderr)
    
    # Calculate interval in seconds
    interval_seconds = parse_duration(args.every)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            
            if args.debug:
                print(f"[DEBUG] Watch iteration {iteration}", file=sys.stderr)
            
            # Get previously seen CVE IDs
            seen_cves = state.get_seen_cves(query_hash)
            
            records = []
            new_cves = set()
            
            # Fetch and normalize CVEs
            for vuln_data in client.search_cves(
                query=args.query,
                days=args.days,
                min_cvss=args.min_cvss,
                severities=args.severity
            ):
                record = normalize_cve(vuln_data)
                
                # Apply filters
                if not filter_record(record, min_cvss=args.min_cvss, severities=args.severity):
                    continue
                
                cve_id = record["cve_id"]
                new_cves.add(cve_id)
                
                # Only include if not previously seen
                if cve_id not in seen_cves:
                    records.append(record)
            
            # Update state with all CVE IDs (seen + new)
            all_cves = seen_cves | new_cves
            state.update_seen_cves(query_hash, all_cves)
            
            # Output new CVEs
            if records:
                output_format = "json" if args.json else "table"
                write_output(records, format=output_format)
            elif not args.once:
                if args.debug:
                    print(f"[DEBUG] No new CVEs found", file=sys.stderr)
            
            # Exit if --once flag is set
            if args.once:
                break
            
            # Wait for next iteration
            if args.debug:
                print(f"[DEBUG] Sleeping for {interval_seconds}s...", file=sys.stderr)
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\nWatch interrupted by user.", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cvewatch",
        description="Monitor and search NVD CVE database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--version", action="version", version=f"cvewatch {__version__}")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search CVEs once")
    search_parser.add_argument("query", help="Search query (keyword)")
    search_parser.add_argument("--days", type=int, required=True, help="Days to look back")
    search_parser.add_argument("--min-cvss", type=float, help="Minimum CVSS score")
    search_parser.add_argument(
        "--severity",
        nargs="+",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity levels"
    )
    search_parser.add_argument("--json", action="store_true", help="Output as NDJSON")
    search_parser.add_argument("--csv", action="store_true", help="Output as CSV")
    
    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Watch for new CVEs")
    watch_parser.add_argument("query", help="Search query (keyword)")
    watch_parser.add_argument("--days", type=int, required=True, help="Days to look back")
    watch_parser.add_argument("--every", required=True, help="Check interval (e.g., 1h, 6h, 24h)")
    watch_parser.add_argument("--min-cvss", type=float, help="Minimum CVSS score")
    watch_parser.add_argument(
        "--severity",
        nargs="+",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity levels"
    )
    watch_parser.add_argument("--json", action="store_true", help="Output as NDJSON")
    watch_parser.add_argument("--once", action="store_true", help="Run one watch cycle and exit")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "search":
        cmd_search(args)
    elif args.command == "watch":
        cmd_watch(args)


if __name__ == "__main__":
    main()
