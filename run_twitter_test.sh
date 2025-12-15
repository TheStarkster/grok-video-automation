#!/bin/bash

# Quick start script for Twitter Automation Detection Test

echo "=========================================="
echo "Twitter Automation Detection Test"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed!"
    echo "   Please install pip first."
    exit 1
fi

echo "✅ pip found"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
if ! python3 -c "import undetected_chromedriver" 2>/dev/null; then
    echo "⚠️  undetected-chromedriver not found"
    echo "📦 Installing dependencies..."
    pip3 install undetected-chromedriver selenium
    echo ""
fi

if ! python3 -c "import selenium" 2>/dev/null; then
    echo "⚠️  selenium not found"
    echo "📦 Installing dependencies..."
    pip3 install selenium
    echo ""
fi

echo "✅ All dependencies installed"
echo ""

# Check if Chrome is installed (Mac-specific check)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ ! -d "/Applications/Google Chrome.app" ]; then
        echo "⚠️  Warning: Chrome not found in /Applications/"
        echo "   Make sure Chrome is installed"
        echo ""
    else
        echo "✅ Chrome browser found"
        echo ""
    fi
fi

# Run the script
echo "=========================================="
echo "Starting Twitter Automation Test..."
echo "=========================================="
echo ""

python3 twitter_selenium_test.py

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="

