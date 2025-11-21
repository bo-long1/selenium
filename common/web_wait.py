"""Web wait utilities with explicit waits for Selenium WebDriver."""

from typing import Union, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Type alias for locator
Locator = Tuple[str, str]


class WebWait:

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initialize WebWait.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Default timeout in seconds (default: 10)
        """
        self.driver = driver
        self.default_timeout = timeout

    # INTERNAL HELPER
    def _wait(self, timeout: int = None) -> WebDriverWait:
        """Get WebDriverWait instance with specified or default timeout."""
        return WebDriverWait(self.driver, timeout or self.default_timeout)

    def _wait_until(self, condition, timeout: int = None, error_msg: str = ""):
        """Execute wait with error handling."""
        try:
            return self._wait(timeout).until(condition)
        except TimeoutException:
            raise TimeoutException(error_msg or f"Timeout after {timeout or self.default_timeout}s")

    def wait_for_element_present(self, locator: Locator, timeout: int = None) -> WebElement:
        """Wait for element to be present in DOM (not necessarily visible)."""
        return self._wait_until(
            EC.presence_of_element_located(locator),
            timeout,
            f"Element {locator} not present within {timeout or self.default_timeout}s"
        )

    def wait_for_element_not_present(self, locator: Locator, timeout: int = None) -> bool:
        """Wait for element to be absent from DOM."""
        return self._wait_until(
            EC.invisibility_of_element_located(locator),
            timeout,
            f"Element {locator} still present after {timeout or self.default_timeout}s"
        )

    def wait_for_element_visible(self, locator: Locator, timeout: int = None) -> WebElement:
        """Wait for element to be visible."""
        return self._wait_until(
            EC.visibility_of_element_located(locator),
            timeout,
            f"Element {locator} not visible within {timeout or self.default_timeout}s"
        )

    def wait_for_element_invisible(self, locator: Locator, timeout: int = None) -> bool:
        """Wait for element to become invisible."""
        return self._wait_until(
            EC.invisibility_of_element_located(locator),
            timeout,
            f"Element {locator} still visible after {timeout or self.default_timeout}s"
        )

    def wait_for_element_clickable(self, locator: Locator, timeout: int = None) -> WebElement:
        """Wait for element to be clickable (visible and enabled)."""
        return self._wait_until(
            EC.element_to_be_clickable(locator),
            timeout,
            f"Element {locator} not clickable within {timeout or self.default_timeout}s"
        )

    def wait_for_element_stale(self, element: WebElement, timeout: int = None) -> bool:
        """Wait for element to become stale (removed from DOM)."""
        return self._wait_until(
            EC.staleness_of(element),
            timeout,
            f"Element did not become stale within {timeout or self.default_timeout}s"
        )

    def wait_for_text_in_element(self, locator: Locator, text: str, timeout: int = None) -> bool:
        """Wait for specific text to appear in element."""
        return self._wait_until(
            EC.text_to_be_present_in_element(locator, text),
            timeout,
            f"Text '{text}' not found in {locator} within {timeout or self.default_timeout}s"
        )

    def wait_for_alert_present(self, timeout: int = None):
        """Wait for alert to be present and return it."""
        return self._wait_until(
            EC.alert_is_present(),
            timeout,
            f"Alert not present within {timeout or self.default_timeout}s"
        )

    def wait_for_frame_and_switch(self, locator: Union[Locator, int, str], timeout: int = None):
        """Wait for frame to be available and switch to it."""
        return self._wait_until(
            EC.frame_to_be_available_and_switch_to_it(locator),
            timeout,
            f"Frame {locator} not available within {timeout or self.default_timeout}s"
        )

    def wait_for_number_of_windows(self, number: int, timeout: int = None) -> bool:
        """Wait for a specific number of windows to be open."""
        return self._wait_until(
            EC.number_of_windows_to_be(number),
            timeout,
            f"Number of windows did not reach {number} within {timeout or self.default_timeout}s"
        )
