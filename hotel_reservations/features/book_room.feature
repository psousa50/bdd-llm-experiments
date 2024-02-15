Feature: Book a room in a hotel

  Scenario: A helpful user
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in Kensington hotel in London, starting in 2024-02-09 and ending in 2024-02-11
        It will be for 2 adults and 1 child.
        """

       And Today is 2024-02-04

       And We have the following hotels in London:
         | Id | Name                                  |
         | 1  | Britannia International Hotel         |
         | 2  | Park Grand London Kensington          |
         | 3  | Park Plaza Westminster Bridge London  |

      When I start a conversation with an Assistant
       And I say "Hi"

      Then The assistant should book a room for Pedro Sousa, in the hotel with id 2, starting in 2024-02-09 and ending in 2024-02-11, for 3 people
       And The conversation should fullfill the following criteria, with a score above 6:
       """
        Greet the user
        Ask for the user name if needed
        Ask for the location of the hotel
        Ask for the check-in date
        Ask for the check-out date
        Ask for the number of guests
        Ask for confirmation before booking
        Book a room for Pedro Sousa, in Kensington hotel, checkin 2024-02-09, checkout 2024-02-11, for 3 guests
       """

  @run
  Scenario: A helpful user, using weekend
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in Britannia International Hotel, for the next weekend.
        It will be for 2 adults and 1 child.
        """

       And Today is 2024-02-04

       And We have the following hotels in London:
         | Id | Name                                  |
         | 34 | Britannia International Hotel         |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      #  Then The assistant should book a room for Pedro Sousa, in the hotel with id 34, starting in 2024-02-09 and ending in 2024-02-11, for 3 people
      Then The conversation should fullfill the following criteria, with a score above 6:
       """
        Ask for the user name if needed
        Ask for the location of the hotel
        Ask for the check-in date
        Ask for the check-out date
        Ask for the number of guests
        Ask for confirmation before booking
        Book a room for Pedro Sousa, in Britannia International Hotel, checkin 2024-02-09, checkout 2024-02-11, for 3 guests
       """

  Scenario: A helpful user, using relative day
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in Britannia International Hotel, starting next Thursay, for 4 days.
        It will be for 2 guests
        """

       And Today is 2024-01-23

       And We have the following hotels in London:
         | Id | Name                                  |
         | 34 | Britannia International Hotel         |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

       Then The assistant should book a room for Pedro Sousa, in the hotel with id 34, starting in 2024-01-25 and ending in 2024-01-29, for 2 people
       Then The conversation should make sense, with a score above 8

  Scenario: A helpful user, using specific dates, no year
     Given I'm a user with the following persona:
        """
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in the Britannia International Hotel, starting in May 2 and ending in May 7
        It will be for 4 guests
        """

       And We have the following hotels in London:
         | Id | Name                                  |
         | 34 | Britannia International Hotel         |

      When I start a conversation with an Assistant
       And I say "I want to book a room"

      Then The assistant should fetch the current year
       And The assistant should book a room for Pedro Sousa, in the hotel with id 34, starting in 2022-05-02 and ending in 2022-05-07, for 4 people
       And The conversation should make sense, with a score above 8
