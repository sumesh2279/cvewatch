"""NVD API 2.0 client with pagination and rate limiting."""

import time
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, Iterator, Dict, Any, List
from urllib.parse import urlencode

import httpx


NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RESULTS_PER_PAGE = 200
MAX_RETRIES = 5
BACKOFF_BASE = 1.0  # seconds
PAGE_DELAY_MIN = 0.2  # 200ms
PAGE_DELAY_MAX = 0.5  # 500ms


class NVDClient:
    """Client for NVD CVE API 2.0."""
    
    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        self.api_key = api_key
        self.debug = debug
        self.session = httpx.Client(timeout=30.0)
    
    def __del__(self):
        """Clean up session."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers including optional API key."""
        headers = {
            "User-Agent": "cvewatch/1.0.0 (https://github.com/yourusername/cvewatch)"
        }
        if self.api_key:
            headers["apiKey"] = self.api_key
        return headers
    
    def _log(self, message: str):
        """Debug logging."""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate backoff delay with jitter."""
        delay = BACKOFF_BASE * (2 ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
    
    def _fetch_page(self, params: Dict[str, Any], start_index: int) -> Dict[str, Any]:
        """Fetch a single page with retries."""
        params["startIndex"] = start_index
        params["resultsPerPage"] = RESULTS_PER_PAGE
        
        url = f"{NVD_API_BASE}?{urlencode(params)}"
        self._log(f"GET {url}")
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, headers=self._build_headers())
                
                # Handle rate limiting
                if response.status_code in (429, 503):
                    if attempt < MAX_RETRIES - 1:
                        delay = self._exponential_backoff(attempt)
                        self._log(f"Rate limited (HTTP {response.status_code}), retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limited after {MAX_RETRIES} retries")
                
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                if attempt < MAX_RETRIES - 1 and e.response.status_code >= 500:
                    delay = self._exponential_backoff(attempt)
                    self._log(f"Server error (HTTP {e.response.status_code}), retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
            
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt < MAX_RETRIES - 1:
                    delay = self._exponential_backoff(attempt)
                    self._log(f"Request error ({e}), retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                raise Exception(f"Request failed: {e}")
        
        raise Exception("Max retries exceeded")
    
    def search_cves(
        self,
        query: str,
        days: int,
        min_cvss: Optional[float] = None,
        severities: Optional[List[str]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Search CVEs with pagination.
        
        Yields raw CVE objects from NVD API.
        """
        # Calculate date window (UTC)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        params = {
            "keywordSearch": query,
            "pubStartDate": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "pubEndDate": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
        
        # Note: NVD API doesn't support direct CVSS/severity filtering
        # We'll filter client-side in normalize.py
        
        start_index = 0
        total_results = None
        
        while True:
            page_data = self._fetch_page(params, start_index)
            
            if total_results is None:
                total_results = page_data.get("totalResults", 0)
                self._log(f"Total results: {total_results}")
            
            vulnerabilities = page_data.get("vulnerabilities", [])
            if not vulnerabilities:
                break
            
            for vuln in vulnerabilities:
                yield vuln
            
            start_index += len(vulnerabilities)
            
            # Check if we've fetched all results
            if start_index >= total_results:
                break
            
            # Client-side delay to avoid rate limits
            time.sleep(random.uniform(PAGE_DELAY_MIN, PAGE_DELAY_MAX))
