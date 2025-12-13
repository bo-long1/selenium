Feature: Example Feature

Background: 
    Given Visit the page http://the-internet.herokuapp.com

Scenario: Example scenario click into the func a/b testing
    When click a/b testing
    Then should see the title "The Internet"

Scenario: Test basic authentication
    When Click to verify basic functionality
    Then Visit with auth "http://admin:admin@the-internet.herokuapp.com/basic_auth"
    And Verify the authentication process

    Scenario Outline: Click to the func Authentication
        When click func Authentication
        And input into the username "<username>" and password "<password>"
        And enter button login
        Then Verify user login success

        Examples:
            | username  | password                |
            | tomsmith  | SuperSecretPassword!    |
            | tomsmith1 | SuperSecretPassword!111 |
