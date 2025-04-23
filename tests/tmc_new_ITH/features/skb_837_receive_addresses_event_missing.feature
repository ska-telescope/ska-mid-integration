@XTP-79283 @XTP-28347 @TEAM_HIMALAYA
Scenario: Fallback to attribute‑read when no change event for attribute receiveAddresses
    Given subarray is in observation state IDLE
    And change event data is EMPTY for attribute receiveAddresses
    When I configure the subarray
    Then Subarray transitions to observation state READY