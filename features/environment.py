"""
Behave environment configuration with automated failure diagnostics.

Features:
- Automatic screenshot capture on test failure
- Browser console log capture on test failure
- Dual logging: console + timestamped file
- Allure report integration
- Debug mode for detailed step-by-step logging
"""
from common.logger import logger, reconfigure_logger_from_settings
from driver.environment_helpers import (
    setup_directories,
    clean_allure_results,
    create_driver,
    close_driver,
    handle_step_failure,
    log_step_start,
    log_step_end,
    log_scenario_details,
    is_step_failed,
)


# ============================================================================
# BEHAVE HOOKS
# ============================================================================
def before_all(context):
    """Initialize test environment: clean old results and setup directories."""
    clean_allure_results()
    setup_directories()
    reconfigure_logger_from_settings()
    print("=" * 80)
    print("Selenium BDD Test Runner")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup: Create WebDriver for the scenario."""
    log_scenario_details(scenario)
    try:
        create_driver(context, scenario.name)
    except Exception as e:
        logger.error(f'Failed to create WebDriver for scenario "{scenario.name}": {e}')
        raise
    logger.info(f"WebDriver created for scenario: {scenario.name}") 

def before_step(context, step):
    """Log step start only in debug mode (formatter shows steps in normal mode)."""
    log_step_start(step)


def after_step(context, step):
    """Capture diagnostics on step failure and log completion."""
    if is_step_failed(step):
        log_step_end(step)
        handle_step_failure(context, step)


def after_scenario(context, scenario):
    """Cleanup: Close WebDriver after scenario."""
    close_driver(context, scenario.name)
    logger.info(f"WebDriver closed for scenario: {scenario.name}")
