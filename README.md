# 🚀 Selenium BDD Framework

> Thread-safe Behave framework with Page Object Model and parallel execution

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.x-green.svg)](https://selenium.dev/)
[![Behave](https://img.shields.io/badge/behave-1.2.6-orange.svg)](https://behave.readthedocs.io/)

---

## 📑 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Reporting](#reporting)
- [Configuration](#configuration)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## ✨ Features

| Feature              | Description                                           |
| -------------------- | ----------------------------------------------------- |
| 🔒 Thread-safe       | Parallel execution without race conditions            |
| 📦 Page Object Model | Maintainable page components with lazy initialization |
| ⚡ Parallel Runner   | Custom runner with ThreadPoolExecutor + subprocess    |
| 📊 Allure Reports    | Interactive HTML reports with history tracking        |
| 📸 Auto Diagnostics  | Screenshots + console logs on failure                 |
| 🎯 Smart Waits       | Custom explicit wait conditions                       |
| 🔧 Multi-env         | JSON config for multiple environments                 |

---

## ⚡ Quick Start

### 1. Setup

````bash
# Clone & install
git clone https://github.com/bo-long1/selenium.git selenium_bdd_threaded
cd selenium_bdd_threaded
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt

# Verify installation
behave features/herokuapp/login_heroku.feature

### System Requirements
- **Python**: 3.11 or higher
- **Git**: For cloning the repository
- **Browser**: Chrome or Edge (automatically managed via webdriver-manager)
- **Java**: 11+ (required for Allure CLI)

### Step 1: Clone the Repository

```bash
# Clone the repository to your local machine
git clone https://github.com/bo-long1/selenium.git selenium_bdd_threaded
cd selenium_bdd_threaded

# Create Virtual Environment
python -m venv venv
## Windows
venv\Scripts\activate
## macOS/Linux
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Install Allure CLI (Optional)
## Windows (via Scoop)
scoop install allure

## macOS
brew install allure

## Linux
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update && sudo apt-get install allure
````

### Step 2: Run Tests

```bash
# Single test
behave features/herokuapp/login_heroku.feature

# Run by scenario line
behave features/herokuapp/login_heroku.feature:23

# With tags
behave --tags @smoke

# Parallel Execution (Recommended)
# Custom runner - subprocess-based isolation
python driver/runner.py --feature herokuapp --mode parallel --workers 4

# How it works:
# Main Process → ThreadPoolExecutor → N workers
#   ├─ Worker 1 → subprocess(behave feature1) → Browser 1
#   ├─ Worker 2 → subprocess(behave feature2) → Browser 2
#   └─ Worker N → subprocess(behave featureN) → Browser N
# → Merge JSON → Convert Allure → Generate HTML

# Sequential
python driver/runner.py --feature herokuapp --mode single

# Specific file custom
## Folder name
python driver/runner.py --feature herokuapp

## Specific file (relative path)
python driver/runner.py --feature herokuapp/check_boxes.feature

## with ./ prefix
python driver/runner.py --feature ./herokuapp/check_boxes.feature
```

### Step 3: View Report

```bash
# Auto-generated at ./allure_report after runner.py
cd allure_report && python -m http.server 8080
# Open: http://localhost:8080

# Manual generation
allure generate allure_results -o allure_report --clean
```

---

## 📁 Project Structure

```
selenium_bdd_threaded/
├── 🔧 config/
│   └── test_setting.json          # Browser config, timeouts, URLs
├── 🚗 driver/
│   ├── driver_factory.py          # WebDriver creation
│   ├── environment_helpers.py     # Hooks, diagnostics, logging
│   └── runner.py                  # ⭐ Parallel execution engine
├── 🛠️ common/
│   ├── logger.py                  # Thread-safe logging
│   ├── utils.py                   # BasePage, load_settings
│   ├── web_actions.py             # Reusable actions
│   ├── web_assertions.py          # Custom assertions
│   └── web_wait.py                # Explicit waits
├── 📄 pages/
│   ├── locator.py                 # Centralized locators
│   ├── heroku.py                  # Page objects
│   └── page_factory.py            # Lazy page initialization
├── 🥒 features/
│   ├── environment.py             # Global hooks
│   ├── herokuapp/
│   │   ├── *.feature              # Gherkin scenarios
│   │   ├── environment.py         # Feature hooks
│   │   └── steps/*.py             # Step definitions
│   └── orange_hrm/
│       └── ...
├── 📊 allure_results/             # JSON results
├── 📈 allure_report/              # HTML report
└── 📝 log_report/                 # Screenshots, logs
```

---

## 📊 Reporting

### Generate Allure Report

```bash
# Auto-generated by runner.py
python driver/runner.py --feature herokuapp --mode parallel --workers 4
# ✅ Report at: ./allure_report

# Manual generation
allure generate allure_results -o allure_report --clean

# Serve locally
cd allure_report && python -m http.server 8080
```

### Install Allure CLI

```bash
npm install -g allure-commandline  # via npm
brew install allure                # macOS
scoop install allure               # Windows
```

Track History & Trends
History is automatically preserved by runner.py. After multiple runs:

Duration Trend - Execution time across runs
History Trend - Pass/fail rate over time
Retry Trend - Flaky test detection

---

## ⚙️ Configuration

Edit `config/config.json` for environment-specific settings:

```json
{
  "dev": {
    "base_url": "https://dev.example.com",
    "browser": "chrome",
    "headless": false,
    "timeout": 10,
    "thread_count": 4
  }
}
```

---

## 🔧 CI/CD Integration

### GitHub Actions Example

```yaml
name: BDD Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: behave --parallel-processes 4 --format json.behave_json --outfile reports/report.json
      - uses: simple-elf/allure-report-action@master
```

---

## 🐛 Troubleshooting

| Issue                 | Solution                                               |
| --------------------- | ------------------------------------------------------ |
| WebDriver not found   | Run `pip install --upgrade webdriver-manager`          |
| Thread conflicts      | Verify thread_count in config matches system resources |
| Reports not generated | Ensure Java is installed for Allure CLI                |
| Tests timeout         | Increase `timeout` value in config.json                |

---

## 📚 Additional Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Selenium Documentation](https://selenium.dev/documentation/)
- [Allure Documentation](https://docs.qameta.io/allure/)

---

## 📄 License

MIT License - See LICENSE file for details
