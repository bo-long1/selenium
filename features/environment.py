"""
Behave environment configuration with automated failure diagnostics.

Features:
- Automatic screenshot capture on test failure
- Browser console log capture on test failure
- Dual logging: console + timestamped file
- Allure report integration
- Debug mode for detailed step-by-step logging
- Thread-safe: Page objects initialized on-demand in steps
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
    close_driver_if_continuing,
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
    """Setup: Create WebDriver and initialize page objects for the scenario."""
    log_scenario_details(scenario)
    create_driver(context, scenario.name)
    try:
        logger.info(f"WebDriver created for scenario: {scenario.name}")
        
    except Exception as e:
        logger.error(f'Failed to initialize scenario "{scenario.name}": {e}')
        raise 

def before_step(context, step):
    """Log step start only in debug mode (formatter shows steps in normal mode)."""
    log_step_start(step)

def after_step(context, step):
    """Capture diagnostics on step failure and log completion."""
    if is_step_failed(step):
        log_step_end(step)
        handle_step_failure(context, step)

def after_scenario(context, scenario):
    """Cleanup: Close WebDriver and clean up page objects after scenario."""
    # Close WebDriver
    close_driver(context, scenario.name)
    logger.info(f"Scenario cleanup completed: {scenario.name}")

def after_feature(context, feature):
    close_driver_if_continuing(context)
