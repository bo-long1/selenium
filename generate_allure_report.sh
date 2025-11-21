#!/bin/bash
# Generate Allure HTML report from existing test results

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESULTS_DIR="$SCRIPT_DIR/allure_results"
REPORT_DIR="$SCRIPT_DIR/allure_report"

echo "=========================================="
echo "📊 Generating Allure Report"
echo "=========================================="
echo ""

if [ ! -d "$RESULTS_DIR" ]; then
    echo "❌ Error: Allure results not found: $RESULTS_DIR"
    echo "Please run tests first: bash run_tests.sh"
    exit 1
fi

if ! command -v allure &> /dev/null; then
    echo "❌ Error: Allure CLI not installed"
    echo "📝 Install: npm install -g allure-commandline"
    exit 1
fi

echo "🔄 Generating report..."
allure generate "$RESULTS_DIR" -o "$REPORT_DIR" --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Report generated successfully!"
    echo "=========================================="
    echo ""
    echo "📁 Location: $REPORT_DIR"
    echo "💡 View: allure serve $RESULTS_DIR"
else
    echo "❌ Failed to generate report"
    exit 1
fi
