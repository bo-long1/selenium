# Define step implementations for the Challenging DOM feature
from behave import given, when, then
from common.web_assertions import WebAssertions
from pages.page_factory import get_heroku_page

@given('Access to the Herokuapp home page')
def step_impl(context):
    get_heroku_page(context).open()

@given('Click to the "{link_text}" link')
def step_impl(context, link_text):
    get_heroku_page(context).click_challenging_dom_link(link_text)

@when('Click the "{button_text}" button')
def step_impl(context, button_text):
    get_heroku_page(context).click_bar_btn(button_text)

@then('Should see the "{button_text}" button')
def step_impl(context, button_text):
    # This step assumes that if we can click the button without exception, it is clickable
    check_name_btn = get_heroku_page(context).get_current_button(button_text)
    WebAssertions().assert_true(
        check_name_btn == button_text,
        f"The button '{button_text}' should be visible and clickable."
    )
