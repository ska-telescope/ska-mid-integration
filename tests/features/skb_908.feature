This test verifies Assign Resources flow with multiple subarrays
@XTP-91092 @XTP-28347 @SKA_mid
Scenario: Verify SKB-908 for assign resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the EMPTY ObsState
    When I assign resources to both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrays are OK
    And the TMC, CSP, SDP subarray 1 and 2 transition to the IDLE obsState

#This test verifies Release Resources flow with multiple subarrays
@XTP-91093 @XTP-28347 @SKA_mid
Scenario: Verify SKB-908 for release resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the IDLE ObsState
    When I release resources from both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrays are OK
    And the TMC, CSP, SDP subarray 1 and 2 transition to the EMPTY obsState