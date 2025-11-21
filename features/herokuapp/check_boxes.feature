Feature: Checkboxes on The Internet Herokuapp

    Background:
        Given I am on "https://the-internet.herokuapp.com/checkboxes"

    @checkbox
    Scenario Outline: Set and verify checkbox state using text labels
        When I set checkbox "<checkbox_label>" to "<desired_state>"
        Then checkbox "<checkbox_label>" should be "<expected_state>"

        Examples:
            | checkbox_label | desired_state | expected_state |
            | checkbox 1     | checked       | checked        |
            | checkbox 2     | unchecked     | unchecked      |
