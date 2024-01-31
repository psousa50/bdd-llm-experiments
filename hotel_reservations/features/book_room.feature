Feature: Book a room in a hotel

  Scenario: A helpful user, using relative dates
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in Kensington hotel in London, for the next weekend.
        It will be for 2 adults and 1 child.
        """

       And Today is 2024-02-04

       And We have the following hotels in London:
         | Id | Name                                  |
         | 1  | Britannia International Hotel         |
         | 2  | Park Grand London Kensington          |
         | 3  | Park Plaza Westminster Bridge London  |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      Then The assistant should fetch the current date
       And The assistant should book a room for Pedro Sousa, in the hotel with id 2, starting in 2024-02-09 and ending in 2024-02-11, for 3 people

  Scenario: A helpful user, using specific dates, no year
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in Paris, starting in May 2 and ending in May 7
        It will be for 4 guests
        """

       And The year is 2023

       And We have the following hotels available:
         | Id | Name                                  | Location |
         | 1  | Britannia International Hotel         | London   |
         | 2  | Park Grand London Kensington          | London   |
         | 3  | Hotel France                          | France   |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      Then The assistant should fetch the current year
       And The assistant should book a room for Pedro Sousa, in the hotel with id 3, starting in 2023-05-02 and ending in 2023-05-07, for 4 people
