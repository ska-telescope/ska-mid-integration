@
Scenario: Verify SKB-837
    Given subarray is in observation state IDLE
    And change event data is EMPTY for attribute receiveAddresses
    When I configure the subarray
    Then Subarray transitions to observation state READY