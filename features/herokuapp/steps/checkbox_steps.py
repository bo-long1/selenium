"""
Step definitions for checkbox interactions on Herokuapp page.

Uses lazy-initialized page objects for thread-safe access.
"""
from behave import given, when, then
from common.web_assertions import WebAssertions
from pages.page_factory import get_heroku_page


@given(u'I am on "{url}"')
def step_open_url(context, url):
    """Navigate to specified URL."""
    get_heroku_page(context).open(url)


@when(u'I set checkbox "{checkbox_label}" to "{desired_state}"')
def step_set_checkbox(context, checkbox_label, desired_state):
    """Set checkbox identified by text label to desired state."""
    get_heroku_page(context).set_checkbox_state(checkbox_label, desired_state)


@then(u'checkbox "{checkbox_label}" should be "{expected_state}"')
def step_verify_checkbox(context, checkbox_label, expected_state):
    """Verify checkbox state by text label."""
    is_selected = get_heroku_page(context).get_checkbox_state(checkbox_label)
    expected = (expected_state.lower() == "checked")
    WebAssertions().assert_equals(
        is_selected,
        expected,
        f"Checkbox '{checkbox_label}' expected '{expected_state}' but was '{'checked' if is_selected else 'unchecked'}'"
    )
