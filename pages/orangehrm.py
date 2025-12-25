"""
OrangeHRM Page Object - Handles OrangeHRM application interactions.
"""

from common.logger import logger
from common.web_actions import WebAction
from common.web_wait import WebWait
from pages.locator import OrangeHRMLoginPageLocators


class OrangeHRMPage(WebAction, WebWait):
    """Page Object for OrangeHRM application."""
    
    def __init__(self, context):
        """Initialize page object with context."""
        self.driver = context.driver
        WebAction.__init__(self, self.driver)
        WebWait.__init__(self, self.driver)
        self.environments = context.environments
    
    def open_login_page(self):
        login_url = self.environments.get('base_url')
        self.driver.get(login_url)
        self.wait_for_page_load()
    
    def enter_username(self, username):
        self.type(OrangeHRMLoginPageLocators.username_field, username, clear_first=True)
    
    def enter_password(self, password):
        self.wait_for_element_visible(OrangeHRMLoginPageLocators.password_field)
        self.type(OrangeHRMLoginPageLocators.password_field, password, clear_first=True)
    
    def click_login_button(self):
        element = self.wait_for_element_clickable(OrangeHRMLoginPageLocators.login_button)
        element.click()
    
    def is_dashboard_displayed(self):
        try:
            dashboard_element = self.wait_for_element_visible(
                OrangeHRMLoginPageLocators.dashboard_header, 
                timeout=10
            )
            return dashboard_element is not None
        except Exception as e:
            return False
    
    def get_error_message(self):
        try:
            error_element = self.wait_for_element_visible(
                OrangeHRMLoginPageLocators.error_message,
                timeout=5
            )
            error_text = error_element.text
            return error_text
        except Exception as e:
            logger.warning(f"No error message found: {str(e)}")
            return ""
    
    def wait_for_page_load(self):
        self.wait_for_element_visible(OrangeHRMLoginPageLocators.username_field, timeout=15)
