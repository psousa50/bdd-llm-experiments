Feature: Find a date from a query

  Scenario: Tomorrow's date
    Given I say
    """
    Today is 2024-04-01. What day is tomorrow?
    """
    When I ask the assistant to find a date
    Then I should see 2024-04-02

  Scenario: Next Thurdsay
    Given I say
    """
    Today is 2024-01-23. What day is next thurday?
    """
    When I ask the assistant to find a date
    Then I should see 2024-01-25

  Scenario: Next Weekend
    Given I say
    """
    Today is 2024-02-05. What day is next weekend?
    """
    When I ask the assistant to find a date
    Then I should see 2024-02-09

  Scenario: The other Weekend
    Given I say
    """
    Today is 2024-02-05. What day is weekend after the next one?
    """
    When I ask the assistant to find a date
    Then I should see 2024-02-16

  Scenario: Next Week
    Given I say
    """
    Today is 2024-01-24. What day is the start of next week?
    """
    When I ask the assistant to find a date
    Then I should see 2024-01-29
