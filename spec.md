# Specs

## Scenario

Given I'm user who want to make a reservation in hotel H3 in London, starting at tomorrow, for 3 days, for 2 guests. My name is Pedro Sousa.
  And I'm a dumb user so I can only answer one quick question at a time.
  And The list of hotels in London is: ["H1", "H2", "H3"]
  And Today is 2022-01-01

When I start a conversation with the Assistant saying that I want to book a room

Then My assistant should make a reservation with the following data:

- hotel: H3
- name: Pedro Sousa
- checkin: 2022-01-02
- checkout: 2022-01-05
- number_of_guests: 2
