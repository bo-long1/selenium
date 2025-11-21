""" Step definitions for checkbox interactions on Herokuapp page."""
from behave import given, when, then
from pages.heroku import HerokuPage
from common.web_assertions import WebAssertions

@given(u'I am on "{url}"')
def step_open_url(context, url):
    HerokuPage.get_instance().open(url)


@when(u'I set checkbox "{checkbox_label}" to "{desired_state}"')
def step_set_checkbox(context, checkbox_label, desired_state):
    """Set checkbox identified by text label to desired state."""
    HerokuPage.get_instance().set_checkbox_state(checkbox_label, desired_state)


@then(u'checkbox "{checkbox_label}" should be "{expected_state}"')
def step_verify_checkbox(context, checkbox_label, expected_state):
    """Verify checkbox state by text label."""
    is_selected = HerokuPage.get_instance().get_checkbox_state(checkbox_label)
    expected = (expected_state.lower() == "checked")
    WebAssertions().assert_equals(is_selected, expected,
        f"Checkbox '{checkbox_label}' expected '{expected_state}' but was '{'checked' if is_selected else 'unchecked'}'")
