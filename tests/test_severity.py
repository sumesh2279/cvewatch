"""Test severity mapping."""

import pytest
from cvewatch.normalize import get_severity_from_score


def test_severity_critical():
    assert get_severity_from_score(9.0) == "Critical"
    assert get_severity_from_score(10.0) == "Critical"
    assert get_severity_from_score(9.8) == "Critical"


def test_severity_high():
    assert get_severity_from_score(7.0) == "High"
    assert get_severity_from_score(8.9) == "High"
    assert get_severity_from_score(7.5) == "High"


def test_severity_medium():
    assert get_severity_from_score(4.0) == "Medium"
    assert get_severity_from_score(6.9) == "Medium"
    assert get_severity_from_score(5.0) == "Medium"


def test_severity_low():
    assert get_severity_from_score(0.1) == "Low"
    assert get_severity_from_score(3.9) == "Low"
    assert get_severity_from_score(2.0) == "Low"


def test_severity_unknown():
    assert get_severity_from_score(None) == "Unknown"
    assert get_severity_from_score(0.0) == "Unknown"
