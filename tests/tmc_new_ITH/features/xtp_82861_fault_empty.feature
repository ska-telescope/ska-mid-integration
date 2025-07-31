#This test covers scenarios where user invokes Restart command as TMC Subarray Node is in FAULT observation state to recover system.
@XTP-82861 @XTP-28348 @XTP-82747 @TEAM_HIMALAYA
Scenario: Test Restart Command when TMC subarray transitions to FAULT observation state
    Given a TMC Subarray transitioned from RESOURCING to FAULT observation state after command failure
    And CSP and SDP in observation state IDLE and EMPTY
    And CSP transitions to observation state EMPTY after resources are released
    When I invoke Restart Command on the TMC Subarray
    Then TMC subarray transitions to observation state EMPTY