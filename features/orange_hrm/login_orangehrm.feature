Feature: login to OrangeHRM application

    Background:
        Given login to the OrangeHRM application

    @login_valid
    Scenario: Login with valid credentials
        When User enters username "admin"
        And User enters password "admin123"
        And User clicks the login button
        Then User should be redirected to the dashboard page

    @login_invalid
    Scenario Outline: Login with invalid credentials
        When User enters username "<username>"
        And User enters password "<password>"
        And User clicks the login button
        Then An error message "<error_message>" should be displayed

        Examples:
            | username | password  | error_message                     |
            | admin    | wrongpass | Invalid credentials               |
            | wronguser| admin123  | Invalid credentials               |
            |          | admin123  | Username cannot be empty          |
            | admin    |           | Password cannot be empty          |