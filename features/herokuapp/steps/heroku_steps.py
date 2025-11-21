""" Step definitions for Herokuapp page interactions."""
from behave import *
from pages.heroku import HerokuPage
from common.web_assertions import WebAssertions


@given('Visit the page {url}')
def step_visit_page(context, url):
    HerokuPage.get_instance().open(url)

@when('click a/b testing')
def step_click_ab_testing(context):
    HerokuPage.get_instance().click_AB_testing()

@then('should see the title "{expected_title}"')
def step_should_see_title(context, expected_title):
    assert expected_title in context.driver.title

@when('input username "{username}" and password "{password}"')
def step_input_username_password(context, username, password):
    HerokuPage.get_instance().input_username_and_pwd(username, password)

@when('click func Authentication')
def step_click_func_auth(context):
    HerokuPage.get_instance().click_login_authentication()

@when('input into the username "{username}" and password "{password}"')
def step_input_func_username_password(context, username, password):
    HerokuPage.get_instance().input_username_and_pwd(username, password)

@when('enter button login')
def step_enter_button_login(context):
    HerokuPage.get_instance().click_btn_login()

@then('Verify user login success')
def step_verify_user_login_success(context):
    text_login_success = HerokuPage.get_instance().verify_subheader()
    WebAssertions().assert_contains(text_login_success, "Welcome to the Secure Area", "Login failed or unexpected subheader text.")

@when('Click to verify basic functionality')
def step_click_basic_auth(context):
    HerokuPage.get_instance().click_basic_authen()

@then('Visit with auth "{auth_url}"')
def step_visit_with_auth(context, auth_url):
    HerokuPage.get_instance().handle_auth_popup(auth_url)

@then('Verify the authentication process')
def step_verify_auth_process(context):
    message = HerokuPage.get_instance().get_message()
    WebAssertions().assert_contains(message, "Congratulations! You must have the proper credentials.", "Authentication success message not found")
