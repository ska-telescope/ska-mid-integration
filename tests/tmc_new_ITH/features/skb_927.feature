Scenario: Test AssignResources with SDP v1.0
    Given subarray is in observation state EMPTY
    When I assign resources with SDP interface v1.0 to the TMC Subarray
    Then AssignResources is invoked on SDP with provided version v1.0