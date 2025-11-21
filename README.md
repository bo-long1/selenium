# Selenium Behave-BDD Framework

Behave BDD framework with Page Object Model, Allure reports, multi-browser support, and parallel execution.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Run tests
behave -f allure_behave.formatter:AllureFormatter -o allure_results features/

# View report
allure serve allure_results
```

## Project Structure

```
├── config/test_setting.json      # Browser config, timeouts, debug_mode
├── driver/                       # WebDriver factory & helpers
├── common/                       # Reusable utilities (logger, web actions, waits)
├── pages/                        # Page objects & locators
├── features/                     # Feature files & step definitions
├── log_report/                   # Runtime logs
├── allure_results/               # Test results (JSON)
└── allure_report/                # Generated HTML report
```

## Running Tests

```bash
# Single feature
behave -f allure_behave.formatter:AllureFormatter -o allure_results features/herokuapp/checkboxes.feature

# All features
behave -f allure_behave.formatter:AllureFormatter -o allure_results features/

# Filter by tag
behave -f allure_behave.formatter:AllureFormatter -o allure_results --tags=@checkbox features/

# Parallel (install behave-parallel first)
pip install behave-parallel
behave-parallel -n 4 -f allure_behave.formatter:AllureFormatter -o allure_results features/
```

## Configuration (config/test_setting.json)

```json
{
  "browser_options": {
    "browser_type": "chrome", // chrome | edge
    "headless": false,
    "debug_mode": false // true = DEBUG logs, false = INFO logs
  },
  "timeouts": {
    "implicit_wait": 10,
    "page_load_timeout": 20
  }
}
```

## Logging

- **INFO** (default): `17-11 - Step: Given I am on login page`
- **DEBUG** (verbose): `2025-11-17 14:23:45 - DEBUG - [MainThread:12345] - Creating chrome WebDriver...`

Enable debug mode in config: `"debug_mode": true`

## Parameterized Locators

```python
# pages/locator.py
class MyPageLocators:
    button_by_text = (By.XPATH, "//button[text()={}]")

# pages/my_page.py
def click_button(self, text):
    locator = super().parameterized_locator(MyPageLocators.button_by_text, text)
    self.wait_for_element_clickable(locator).click()
```

## Parallel Execution Best Practices

- ✅ Use `context.driver` (per-scenario WebDriver)
- ✅ Enable `debug_mode: true` to see thread IDs
- ❌ Don't share WebDriver or singleton Page objects across threads

## Common Issues

| Issue                                           | Solution                                                                   |
| ----------------------------------------------- | -------------------------------------------------------------------------- |
| `'tuple' object is not callable`                | Locator is static tuple, use `@staticmethod` or `parameterized_locator()`  |
| `'tuple' object has no attribute 'is_selected'` | Use `driver.find_element(*locator)` or `wait_for_element_present(locator)` |
| Edge driver fails offline                       | Install `msedgedriver.exe` manually or switch to Chrome                    |
| Logger shows DEBUG despite INFO                 | Delete `__pycache__` folders and restart                                   |

## Allure Installation

```bash
npm install -g allure-commandline
# or
scoop install allure
```

---

**Happy Testing!** 🚀
# selenium
