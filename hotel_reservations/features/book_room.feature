Feature: Book a room in a hotel

  Scenario: A helpful user, using relative dates
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in a Hotel in London, for the next weekend.
        It will be for 2 adults and 1 child.
        Any Hotel in London will do.
        """

       And Today is 2024-02-01

       And We have the following hotels in London:
         | Id | Name       |
         | 1  | Hotel UK 1 |
         | 2  | Hotel UK 2 |
         | 3  | Hotel UK 3 |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      Then The assistant should fetch the current date
       And The assistant should book a room for Pedro Sousa, in the hotel with id 1, starting in 2024-02-02 and ending in 2024-02-04, for 3 people

  Scenario: A helpful user, using specific dates, no year
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in a Hotel UK 3, starting in May 2 and ending in May 7
        It will be for 4 guests
        Any Hotel in London will do.
        """

       And The year is 2023

       And We have the following hotels in London:
         | Id | Name       |
         | 1  | Hotel UK 1 |
         | 2  | Hotel UK 2 |
         | 3  | Hotel UK 3 |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      Then The assistant should fetch the current year
       And The assistant should book a room for Pedro Sousa, in the hotel with id 3, starting in 2023-05-02 and ending in 2023-05-07, for 4 people
