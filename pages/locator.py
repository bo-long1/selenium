"""Locators for the-internet.herokuapp.com pages"""
from selenium.webdriver.common.by import By

class LoginPageLocators:
    """Locators for the-internet.herokuapp.com login page"""
    ab_testing = (By.XPATH, "(//a[normalize-space()='A/B Testing'])")
    authentication = (By.XPATH, "//a[normalize-space()='Form Authentication']")
    username = (By.XPATH, "//input[@id='username']")
    password = (By.XPATH, "//input[@id='password']")
    btn_login = (By.XPATH, "//button[@type='submit']")
    subheader = (By.XPATH, "//h4[contains(text(), 'Welcome to the Secure Area')]")
    basic_auth = (By.XPATH, "//a[normalize-space()='Basic Auth']")
    message = (By.XPATH, "//p[contains(text(),'Congratulations! You must have the proper credenti')]")

class CheckboxPageLocators:
    """Locators for the checkbox page"""
    check_box = (By.CSS_SELECTOR, "input[type='checkbox']")
    check_box_by_text = (By.XPATH, "//form[@id='checkboxes']//input[@type='checkbox'][{}]")

class ChallengingDOMPageLocators:
    """Locators for the Challenging DOM page"""
    challenging_dom_link = (By.XPATH, "//a[normalize-space()='{}']")
    bar_button = (By.XPATH, "//a[text()='{}']")


class OrangeHRMLoginPageLocators:
    """Locators for OrangeHRM login page - Priority: ID > CSS > XPath"""
    username_field = (By.NAME, "username")
    password_field = (By.NAME, "password")
    login_button = (By.CSS_SELECTOR, "[class*='orangehrm-login-button']")
    error_message = (By.CSS_SELECTOR, "p.oxd-text.oxd-text--p.oxd-alert-content-text")
    dashboard_header = (By.CSS_SELECTOR, "h6.oxd-text.oxd-text--h6.oxd-topbar-header-breadcrumb-module")
    dashboard_menu = (By.XPATH, "//span[text()='Dashboard']")
    user_dropdown = (By.CSS_SELECTOR, "p.oxd-userdropdown-name")
    dashboard_title = (By.XPATH, "//h6[text()='Dashboard']")
