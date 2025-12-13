#!/bin/bash
# Generate Allure HTML report from existing test results
# Preserves history from previous reports for trend tracking

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESULTS_DIR="$SCRIPT_DIR/allure_results"
REPORT_DIR="$SCRIPT_DIR/allure_report"
HISTORY_DIR="$REPORT_DIR/history"

echo "=========================================="
echo "📊 Generating Allure Report"
echo "=========================================="
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "❌ Error: Allure results not found: $RESULTS_DIR"
    echo "Please run tests first:"
    echo "  python driver/runner.py --feature herokuapp --mode parallel --workers 4"
    exit 1
fi

# Check if Allure CLI is installed
if ! command -v allure &> /dev/null; then
    echo "❌ Error: Allure CLI not installed"
    echo "📝 Install: npm install -g allure-commandline"
    exit 1
fi

# Preserve history from previous report
if [ -d "$HISTORY_DIR" ]; then
    echo "📜 Preserving history from previous report..."
    cp -r "$HISTORY_DIR" "$RESULTS_DIR/history"
    echo "✅ History preserved"
else
    echo "📝 No previous history found (first run)"
fi

echo ""
echo "🔄 Generating report..."
allure generate "$RESULTS_DIR" -o "$REPORT_DIR" --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Report generated successfully!"
    echo "=========================================="
    echo ""
    echo "📁 Location: $REPORT_DIR"
    echo "📈 View trends: Open Graphs tab in report"
    echo "🚀 Serve locally:"
    echo "   cd $REPORT_DIR && python -m http.server 8080"
    echo "   Open: http://localhost:8080"
else
    echo "❌ Failed to generate report"
    exit 1
fi
