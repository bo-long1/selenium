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
    check_box_by_text = (By.XPATH, "//form//input[@type='checkbox' and following-sibling::text()[normalize-space()='{}']]")
