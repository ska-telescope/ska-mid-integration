Feature: test subarray command triggered transitions

  This feature covers all valid state transitions for a subarray 1
  that are triggered by commands, excluding Abort, Restart and the operational
  states (On, Off, Standby).

  Each scenario covers one or more transitions triggered by a Tango
  command; each scenario covers transition from a quiescent state to
  the subsequent quiescent state (i.e. from the starting state to
  a transitional one, followed by the transition to the subsequent
  quiescent state).

  Background:
    Given the telescope is in ON state
    Given the subarray 1 can be used

  Scenario: EMPTY to RESOURCING to IDLE - CMD AssignResources (6)
    Given the subarray 1 is in the EMPTY state
    When the AssignResources command is sent to the subarray 1
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the IDLE state
    Then the central node longRunningCommand should be terminated
  # TODO we send the command to the subarray and
  #  check the LRC of the central node?
  # TODO rewrite the last step as
  # Then the longRunningCommand successfully completes

  Scenario: IDLE to CONFIGURING to READY - CMD Configure (16)
    Given the subarray 1 is in the IDLE state
    When the Configure command is sent to the subarray 1
    Then the subarray 1 should transition to the CONFIGURING state
    Then the subarray 1 should transition to the READY state
    Then the subarray 1 longRunningCommand should be terminated

  Scenario: IDLE to RESOURCING to IDLE - CMD AssignResources (18)
    Given the subarray 1 is in the IDLE state
    When the AssignResources command is sent to the subarray 1
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the IDLE state
    Then the central node longRunningCommand should be terminated

  Scenario: IDLE to RESOURCING to EMPTY - CMD ReleaseResources (17)
    Given the subarray 1 is in the IDLE state
    When the ReleaseResources command is sent to the subarray 1
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the EMPTY state

  Scenario: READY to SCANNING to READY- CMD Scan (9)
    Given the subarray 1 is in the READY state
    When the Scan command is sent to the subarray 1
    Then the subarray 1 should transition to the SCANNING state
    Then the subarray 1 should transition to the READY state
    Then the subarray 1 longRunningCommand should be terminated

  Scenario: READY to IDLE - CMD End (10)
    Given the subarray 1 is in the READY state
    When the End command is sent to the subarray 1
    Then the subarray 1 should transition to the IDLE state

  Scenario: READY to CONFIGURING to READY - CMD Configure (13)
    Given the subarray 1 is in the READY state
    When the Configure command is sent to the subarray 1
    Then the subarray 1 should transition to the CONFIGURING state
    Then the subarray 1 should transition to the READY state
    Then the subarray 1 longRunningCommand should be terminated

  Scenario: SCANNING to READY - CMD End Scan (17)
    Given the subarray 1 is in the SCANNING state
    When the Endscan command is sent to the subarray 1
    Then the subarray 1 should transition to the READY state

