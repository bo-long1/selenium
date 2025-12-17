Feature: testing challenging DOM elements on the Herokuapp

    Background: 
        Given Access to the Herokuapp home page

    @test_challenging_1
    Scenario: Interact with challenging DOM elements
        Given Click to the "Challenging DOM" link
        When Click the "foo" button
        Then Should see the "baz" button

    @test_challenging_2
    Scenario Outline: Verify dynamic button names
        Given Click to the "Challenging DOM" link
        When Click the "<button_text>" button
        Then Should see the "<expected_button>" button

        Examples:
            | button_text | expected_button |
            | foo         | baz             |
            | bar         | foo             |
            | baz         | bar             |
