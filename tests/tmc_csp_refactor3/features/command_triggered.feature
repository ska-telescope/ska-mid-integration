Feature: test subarray command triggered transitions

This feature covers all valid state transitions for a subarray 1, 
focusing on command triggered transitions. Each scenario covers one or more
transitions triggered by a Tango command; the transitions are the ones
that will lead to the next quiescent state (the transition to the final
quiescent state + the transitions to the intermediate transient states).

Background:
  Given the telescope is in ON state
  Given the subarray 1 can be used

Scenario: EMPTY to RESOURCING to IDLE - CMD AssignResources (6)
  Given the subarray 1 is in the EMPTY state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the IDLE state
  Then the central node longRunningCommand should be terminated
  # TODO we send the command to the subarray and check the LRC of the central node?

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


