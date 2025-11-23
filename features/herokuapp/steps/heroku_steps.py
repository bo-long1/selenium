"""
Step definitions for Herokuapp page interactions.

Uses lazy-initialized page objects for thread-safe access.
"""
from behave import given, when, then
from common.web_assertions import WebAssertions
from pages.page_factory import get_heroku_page


@given('Visit the page {url}')
def step_visit_page(context, url):
    """Navigate to the specified URL."""
    get_heroku_page(context).open(url)

@when('click a/b testing')
def step_click_ab_testing(context):
    """Click on A/B Testing link."""
    get_heroku_page(context).click_AB_testing()

@then('should see the title "{expected_title}"')
def step_should_see_title(context, expected_title):
    """Verify page title contains expected text."""
    actual_title = context.driver.title
    WebAssertions().assert_contains(
        actual_title,
        expected_title,
        f"Expected title to contain '{expected_title}' but got '{actual_title}'"
    )


@when('click func Authentication')
def step_click_func_auth(context):
    """Click on Form Authentication link."""
    get_heroku_page(context).click_login_authentication()

@when('input username "{username}" and password "{password}"')
def step_input_username_password(context, username, password):
    """Input username and password into login form."""
    get_heroku_page(context).input_username_and_pwd(username, password)

@when('input into the username "{username}" and password "{password}"')
def step_input_func_username_password(context, username, password):
    """Input username and password into form authentication."""
    get_heroku_page(context).input_username_and_pwd(username, password)

@when('enter button login')
def step_enter_button_login(context):
    """Click login button."""
    get_heroku_page(context).click_btn_login()

@then('Verify user login success')
def step_verify_user_login_success(context):
    """Verify successful login by checking secure area subheader."""
    subheader_text = get_heroku_page(context).verify_subheader()
    WebAssertions().assert_contains(
        subheader_text,
        "Welcome to the Secure Area",
        "Login failed or unexpected subheader text."
    )

@when('Click to verify basic functionality')
def step_click_basic_auth(context):
    """Click on Basic Auth link."""
    get_heroku_page(context).click_basic_authen()

@then('Visit with auth "{auth_url}"')
def step_visit_with_auth(context, auth_url):
    """Navigate to URL with embedded authentication credentials."""
    get_heroku_page(context).handle_auth_popup(auth_url)

@then('Verify the authentication process')
def step_verify_auth_process(context):
    """Verify authentication success message."""
    message = get_heroku_page(context).get_message()
    WebAssertions().assert_contains(
        message,
        "Congratulations! You must have the proper credentials.",
        "Authentication success message not found"
    )
