#!/bin/bash
set -e

echo "🧪 Running comprehensive cvewatch tests..."
echo ""

# Set PATH to include user Python bin
export PATH="/Users/sumeshadiyapurath/Library/Python/3.9/bin:$PATH"

echo "1️⃣  Version check"
cvewatch --version
echo ""

echo "2️⃣  Help output"
cvewatch search --help | head -5
echo ""

echo "3️⃣  Search test (table)"
echo "   Searching for 'linux kernel' CVEs..."
cvewatch search "linux kernel" --days 3 --severity critical | head -10
echo ""

echo "4️⃣  Search test (JSON)"
echo "   Output format: NDJSON"
cvewatch search "microsoft" --days 3 --json | head -2
echo ""

echo "5️⃣  Watch test (--once)"
echo "   Testing state tracking..."
cvewatch watch "test query" --days 3 --every 1h --once > /dev/null
cvewatch watch "test query" --days 3 --every 1h --once
echo "   (No output = state tracking works! ✅)"
echo ""

echo "6️⃣  Unit tests"
pytest tests/ -v --tb=short | tail -20
echo ""

echo "✅ All tests complete!"
