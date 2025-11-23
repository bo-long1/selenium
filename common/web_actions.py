"""Web actions helper - common Selenium interactions with explicit waits."""

import time
from typing import Optional, Tuple, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from common.web_wait import WebWait

# Type alias
Locator = Tuple[str, str]


class WebAction:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initialize WebAction.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Default timeout for waits in seconds (default: 10)
        """
        self.driver = driver
        self.wait = WebWait(driver, timeout)
        self.actions = ActionChains(driver)


    # INTERNAL HELPERS
    def _find_element(self, locator: Locator, wait_visible: bool = True) -> WebElement:
        """Find element with explicit wait."""
        if wait_visible:
            return self.wait.wait_for_element_visible(locator)
        return self.wait.wait_for_element_present(locator)


    # CLICK ACTIONS
    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Click element after waiting for it to be clickable."""
        element = self.wait.wait_for_element_clickable(locator, timeout)
        element.click()
        return element

    def double_click(self, locator: Locator) -> None:
        """Double-click on element."""
        element = self._find_element(locator)
        self.actions.double_click(element).perform()

    def right_click(self, locator: Locator) -> None:
        """Right-click (context menu) on element."""
        element = self._find_element(locator)
        self.actions.context_click(element).perform()

    def click_and_hold(self, locator: Locator) -> None:
        """Click and hold on element."""
        element = self._find_element(locator)
        self.actions.click_and_hold(element).perform()


    # TYPING ACTIONS
    def type(self, locator: Locator, text: str, clear_first: bool = True) -> None:
        """Type text into element."""
        element = self._find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def clear(self, locator: Locator) -> None:
        """Clear input element."""
        element = self._find_element(locator)
        element.clear()

    def enter_each_char(self, locator: Locator, text: str, delay: float = 0.1) -> None:
        element = self._find_element(locator)
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(delay)


    # GET ELEMENT PROPERTIES
    def get_text(self, locator: Locator) -> str:
        """Get visible text from element."""
        element = self._find_element(locator)
        return element.text

    def get_attribute(self, locator: Locator, attribute: str) -> str:
        """Get element attribute value."""
        element = self._find_element(locator)
        return element.get_attribute(attribute)

    def get_value(self, locator: Locator) -> str:
        """Get input element value."""
        return self.get_attribute(locator, 'value')


    # ELEMENT STATE CHECKS
    def is_displayed(self, locator: Locator) -> bool:
        """Check if element is displayed."""
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except (NoSuchElementException, TimeoutException):
            return False

    def is_enabled(self, locator: Locator) -> bool:
        """Check if element is enabled."""
        try:
            element = self._find_element(locator, wait_visible=False)
            return element.is_enabled()
        except (NoSuchElementException, TimeoutException):
            return False

    def is_selected(self, locator: Locator) -> bool:
        """Check if element is selected."""
        try:
            element = self._find_element(locator)
            return element.is_selected()
        except (NoSuchElementException, TimeoutException):
            return False


    # DROPDOWN / SELECT ACTIONS
    def select_by_text(self, locator: Locator, text: str) -> None:
        """Select dropdown option by visible text."""
        element = self._find_element(locator)
        Select(element).select_by_visible_text(text)

    def select_by_value(self, locator: Locator, value: str) -> None:
        """Select dropdown option by value attribute."""
        element = self._find_element(locator)
        Select(element).select_by_value(value)

    def select_by_index(self, locator: Locator, index: int) -> None:
        """Select dropdown option by index."""
        element = self._find_element(locator)
        Select(element).select_by_index(index)

    def get_selected_option_text(self, locator: Locator) -> str:
        """Get currently selected option text."""
        element = self._find_element(locator)
        return Select(element).first_selected_option.text


    # MOUSE ACTIONS
    def hover(self, locator: Locator) -> None:
        """Hover over element."""
        element = self._find_element(locator)
        self.actions.move_to_element(element).perform()

    def drag_and_drop(self, source_locator: Locator, target_locator: Locator) -> None:
        """Drag element from source to target."""
        source = self._find_element(source_locator)
        target = self._find_element(target_locator)
        self.actions.drag_and_drop(source, target).perform()


    # SCROLL ACTIONS
    def scroll_to_element(self, locator: Locator) -> None:
        """Scroll element into view."""
        element = self._find_element(locator, wait_visible=False)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_top(self) -> None:
        """Scroll to top of page."""
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


    # CHECKBOX / RADIO ACTIONS
    def check(self, locator: Locator) -> None:
        """Check checkbox if not already checked."""
        element = self._find_element(locator)
        if not element.is_selected():
            element.click()

    def uncheck(self, locator: Locator) -> None:
        """Uncheck checkbox if checked."""
        element = self._find_element(locator)
        if element.is_selected():
            element.click()

    def toggle(self, locator: Locator) -> None:
        """Toggle checkbox state."""
        element = self._find_element(locator)
        element.click()


    # FILE UPLOAD
    def upload_file(self, locator: Locator, file_path: str) -> None:
        """Upload file to input element."""
        element = self._find_element(locator, wait_visible=False)
        element.send_keys(file_path)


    # ALERT HANDLING
    def accept_alert(self, timeout: int = None) -> None:
        """Accept JavaScript alert."""
        alert = self.wait.wait_for_alert_present(timeout)
        alert.accept()

    def dismiss_alert(self, timeout: int = None) -> None:
        """Dismiss JavaScript alert."""
        alert = self.wait.wait_for_alert_present(timeout)
        alert.dismiss()

    def get_alert_text(self, timeout: int = None) -> str:
        """Get alert text."""
        alert = self.wait.wait_for_alert_present(timeout)
        return alert.text

    def type_in_alert(self, text: str, timeout: int = None) -> None:
        """Type in JavaScript prompt."""
        alert = self.wait.wait_for_alert_present(timeout)
        alert.send_keys(text)
        alert.accept()


    # MULTIPLE ELEMENTS
    def find_elements(self, locator: Locator) -> List[WebElement]:
        """Find all matching elements."""
        self.wait.wait_for_element_present(locator)
        return self.driver.find_elements(*locator)

    def get_element_count(self, locator: Locator) -> int:
        """Get count of matching elements."""
        try:
            return len(self.find_elements(locator))
        except (NoSuchElementException, TimeoutException):
            return 0


    # OPEN NEW TAB
    def open_new_tab(self, url: str) -> None:
        """Open a new browser tab with the specified URL."""
        self.driver.execute_script(f"window.open('{url}', '_blank');") 

    def switch_to_tab(self, index: int) -> None:
        """Switch to browser tab by index."""
        tabs = self.driver.window_handles
        if index < 0 or index >= len(tabs):
            raise IndexError(f"Tab index {index} out of range.")
        self.driver.switch_to.window(tabs[index])

    def close_current_tab(self) -> None:
        """Close the current browser tab."""
        self.driver.close()


    # iFRAME HANDLING
    def switch_to_iframe(self, locator: Locator) -> None:
        """Switch to iframe by locator."""
        iframe = self._find_element(locator)
        self.driver.switch_to.frame(iframe)

    def switch_to_default_content(self) -> None:
        """Switch back to the default content from iframe."""
        self.driver.switch_to.default_content()

    def switch_to_parent_frame(self) -> None:
        """Switch to the parent frame of the current iframe."""
        self.driver.switch_to.parent_frame()


    # WINDOW HANDLING
    def switch_to_window(self, handle: str) -> None:
        """Switch to window by handle."""
        self.driver.switch_to.window(handle)

    def get_current_window_handle(self) -> str:
        """Get current window handle."""
        return self.driver.current_window_handle
    
    def open_new_window(self, url: str) -> None:
        """Open a new browser window with the specified URL."""
        self.driver.execute_script(f"window.open('{url}', '_blank', 'noopener,noreferrer');")

    def close_current_window(self) -> None:
        """Close the current browser window."""
        self.driver.close()

    def open_incognito_window(self, url: str) -> None:
        """Open a new incognito browser window with the specified URL."""
        self.driver.execute_script(f"window.open('{url}', '_blank', 'noopener,noreferrer');")

    def switch_to_incognito_window(self, handle: str) -> None:
        """Switch to incognito window by handle."""
        self.driver.switch_to.window(handle)

    def close_incognito_window(self) -> None:
        """Close the current incognito window."""
        self.driver.close()

    def parameterized_locator(self, locator_tpl, *args, **kwargs):
        """
            - callable: return (By, value) when called with args
            - tuple: (By, template) -> format with args/kwargs
        """
        if callable(locator_tpl):
            return locator_tpl(*args, **kwargs)
        if isinstance(locator_tpl, tuple) and len(locator_tpl) == 2:
            by, template = locator_tpl
            return (by, template.format(*args, **kwargs))
        raise TypeError("Unsupported locator template")
