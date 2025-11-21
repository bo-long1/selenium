""" Login Page Object Model for Herokuapp """

from common.logger import logger
from common.web_actions import WebAction
from common.web_wait import WebWait
from pages.locator import LoginPageLocators, CheckboxPageLocators


class HerokuPage(WebAction, WebWait):
    def __init__(self, driver):
        WebAction.__init__(self, driver)
        WebWait.__init__(self, driver)
        self.driver = driver

    _instance = None

    @classmethod
    def set_driver(cls, driver):
        cls._instance = cls(driver)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("Driver not set. Call set_driver() first.")
        return cls._instance

    def open(self, url):
        self.driver.get(url)

    def click_AB_testing(self):
        element = self.wait_for_element_clickable(LoginPageLocators.ab_testing)
        element.click()

    def click_basic_authen(self):
        element = self.wait_for_element_clickable(LoginPageLocators.basic_auth)
        element.click()

    def handle_auth_popup(self, url):
        self.driver.get(url)

    def get_message(self):
        element = self.wait_for_element_visible(LoginPageLocators.message)
        return element.text

    def click_login_authentication(self):
        self.click(LoginPageLocators.authentication)

    def input_username_and_pwd(self, username, password):
        """Input username and password."""
        self.type(LoginPageLocators.username, username, clear_first=True)
        self.type(LoginPageLocators.password, password, clear_first=True)

    def click_btn_login(self):
        element = self.wait_for_element_clickable(LoginPageLocators.btn_login)
        element.click()

    def verify_subheader(self):
        element = self.wait_for_element_present(LoginPageLocators.subheader)
        return element.text

    def get_checkbox_state(self, text):
        """Get current state of checkbox."""
        locator = super().parameterized_locator(CheckboxPageLocators.check_box_by_text, text)
        checkbox = self.wait_for_element_present(locator)
        return checkbox.is_selected()

    def set_checkbox_state(self, text, desired_state):
        """Set checkbox to desired state (checked/unchecked)."""
        locator = super().parameterized_locator(CheckboxPageLocators.check_box_by_text, text)
        checkbox = self.wait_for_element_present(locator)
        current = checkbox.is_selected()
        target = (desired_state.strip().lower() == "checked")
        if current != target:
            logger.debug(f"Toggling checkbox '{text}' from {current} to {target}")
            checkbox.click()
        return checkbox.is_selected()
