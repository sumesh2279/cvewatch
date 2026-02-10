"""Normalize NVD API responses to simplified CVE records."""

from typing import Optional, Dict, Any, List
from datetime import datetime


def get_severity_from_score(score: Optional[float]) -> str:
    """Map CVSS score to severity level."""
    if score is None:
        return "Unknown"
    if score >= 9.0:
        return "Critical"
    elif score >= 7.0:
        return "High"
    elif score >= 4.0:
        return "Medium"
    elif score >= 0.1:
        return "Low"
    else:
        return "Unknown"


def extract_cvss_score(metrics: Dict[str, Any]) -> Optional[float]:
    """Extract CVSS score, preferring v3.1 > v3.0 > v2.0."""
    # Try CVSS v3.1
    if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
        return metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
    
    # Try CVSS v3.0
    if "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
        return metrics["cvssMetricV30"][0]["cvssData"]["baseScore"]
    
    # Try CVSS v2.0
    if "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
        return metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]
    
    return None


def extract_description(descriptions: List[Dict[str, Any]]) -> str:
    """Extract English description."""
    for desc in descriptions:
        if desc.get("lang") == "en":
            # Single-line format
            return desc.get("value", "").replace("\n", " ").strip()
    
    # Fallback to first description
    if descriptions:
        return descriptions[0].get("value", "").replace("\n", " ").strip()
    
    return ""


def extract_references(references: List[Dict[str, Any]]) -> List[str]:
    """Extract reference URLs."""
    urls = []
    for ref in references:
        url = ref.get("url")
        if url:
            urls.append(url)
    return urls


def normalize_cve(vuln_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize NVD CVE JSON to simplified record.
    
    Returns:
        {
            "cve_id": str,
            "published": str (ISO8601 with Z),
            "last_modified": str (ISO8601 with Z),
            "description": str,
            "cvss_score": float | None,
            "severity": str,
            "references": List[str]
        }
    """
    cve = vuln_data.get("cve", {})
    
    cve_id = cve.get("id", "UNKNOWN")
    published = cve.get("published", "")
    last_modified = cve.get("lastModified", "")
    
    # Extract descriptions
    descriptions = cve.get("descriptions", [])
    description = extract_description(descriptions)
    
    # Extract CVSS score
    metrics = cve.get("metrics", {})
    cvss_score = extract_cvss_score(metrics)
    severity = get_severity_from_score(cvss_score)
    
    # Extract references
    references_data = cve.get("references", [])
    references = extract_references(references_data)
    
    return {
        "cve_id": cve_id,
        "published": published,
        "last_modified": last_modified,
        "description": description,
        "cvss_score": cvss_score,
        "severity": severity,
        "references": references
    }


def filter_record(
    record: Dict[str, Any],
    min_cvss: Optional[float] = None,
    severities: Optional[List[str]] = None
) -> bool:
    """
    Check if record passes filters.
    
    Returns True if record should be included.
    """
    # CVSS filter
    if min_cvss is not None:
        if record["cvss_score"] is None or record["cvss_score"] < min_cvss:
            return False
    
    # Severity filter
    if severities:
        # Normalize severity filter to title case
        normalized_severities = [s.title() for s in severities]
        if record["severity"] not in normalized_severities:
            return False
    
    return True
