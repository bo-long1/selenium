"""
Defination Herokuapp Page.
"""

from common.logger import logger
from common.web_actions import WebAction
from common.web_wait import WebWait
from pages.locator import ChallengingDOMPageLocators, LoginPageLocators, CheckboxPageLocators


class HerokuPage(WebAction, WebWait):
    
    def __init__(self, context):
        """Initialize page object with context."""
        self.driver = context.driver
        WebAction.__init__(self, self.driver)
        WebWait.__init__(self, self.driver)
        self.environments = context.environments

    def open(self):
        self.driver.get(self.environments['base_url'])

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
        """Get current state of checkbox by index (e.g., 'checkbox 1' -> index 1)."""
        index = text.split()[-1]  # Extract number from 'checkbox 1'
        locator = super().parameterized_locator(CheckboxPageLocators.check_box_by_text, index)
        checkbox = self.wait_for_element_present(locator)
        return checkbox.is_selected()

    def set_checkbox_state(self, text, desired_state):
        """Set checkbox to desired state (checked/unchecked)."""
        index = text.split()[-1]  # Extract number from 'checkbox 1'
        locator = super().parameterized_locator(CheckboxPageLocators.check_box_by_text, index)
        checkbox = self.wait_for_element_present(locator)
        current = checkbox.is_selected()
        target = (desired_state.strip().lower() == "checked")
        if current != target:
            logger.debug(f"Toggling checkbox '{text}' from {current} to {target}")
            checkbox.click()
        return checkbox.is_selected()

    def click_link_by_text(self, link_text):
        """Click any link by its text."""
        locator = super().parameterized_locator(CheckboxPageLocators.link_by_text, link_text)
        element = self.wait_for_element_clickable(locator)
        element.click()

    def click_challenging_dom_link(self, link_text):
        locator = super().parameterized_locator(ChallengingDOMPageLocators.challenging_dom_link, link_text)
        element = self.wait_for_element_clickable(locator)
        element.click()

    def click_bar_btn(self, btn_text):
        locator = super().parameterized_locator(ChallengingDOMPageLocators.bar_button, btn_text)
        element = self.wait_for_element_clickable(locator)
        element.click()

    def get_current_button(self, btn_text):
        locator = super().parameterized_locator(ChallengingDOMPageLocators.bar_button, btn_text)
        element = self.wait_for_element_visible(locator)
        return element.text
