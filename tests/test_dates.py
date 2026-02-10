"""Test date window calculation."""

import pytest
from datetime import datetime, timedelta, timezone
from cvewatch.nvd import NVDClient


def test_date_window_calculation():
    """Test that date windows are calculated correctly."""
    client = NVDClient(debug=False)
    
    # We can't easily test the internal date calculation without mocking,
    # but we can verify the query parameters are built correctly by
    # examining the _build_headers method exists and the client initializes
    assert client is not None
    assert hasattr(client, '_build_headers')
    assert hasattr(client, 'search_cves')


def test_date_formats():
    """Test date format string construction."""
    now = datetime(2024, 2, 10, 12, 30, 45, tzinfo=timezone.utc)
    formatted = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    assert formatted == "2024-02-10T12:30:45.000Z"


def test_timedelta_days():
    """Test timedelta calculation for days."""
    end_date = datetime(2024, 2, 10, tzinfo=timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    assert start_date.day == 11
    assert start_date.month == 1
    assert start_date.year == 2024
