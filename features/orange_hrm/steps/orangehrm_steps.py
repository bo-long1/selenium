"""
Step definitions for OrangeHRM login functionality.
"""
from behave import given, when, then
from common.web_assertions import WebAssertions
from pages.page_factory import get_orangehrm_page


@given('login to the OrangeHRM application')
def step_open_orangehrm(context):
    get_orangehrm_page(context).open_login_page()


@when('User enters username "{username}"')
def step_enter_username(context, username):
    get_orangehrm_page(context).enter_username(username)


@when('User enters password "{password}"')
def step_enter_password(context, password):
    get_orangehrm_page(context).enter_password(password)


@when('User clicks the login button')
def step_click_login_button(context):
    get_orangehrm_page(context).click_login_button()


@then('User should be redirected to the dashboard page')
def step_verify_dashboard(context):
    WebAssertions().assert_true(
        get_orangehrm_page(context).is_dashboard_displayed(),
        "Dashboard page is not displayed after login"
    )


@then('An error message "{error_message}" should be displayed')
def step_verify_error_message(context, error_message):
    """Verify error message is displayed."""
    actual_error = get_orangehrm_page(context).get_error_message()
    WebAssertions().assert_contains(
        actual_error,
        error_message,
        f"Expected error message to contain '{error_message}' but got '{actual_error}'"
    )
