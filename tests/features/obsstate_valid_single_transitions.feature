# Feature: subarray 001 State Transitions - Command Triggered

This feature covers all valid state transitions for a subarray 001, focusing only on command-triggered transitions.
Each scenario represents a single transition triggered by a command (CMD).
Operational states and transitions are also excluded.

Background:
  Given the telescope is in ON state
  Given the subarray 001 can be used

Scenario: EMPTY to RESOURCING - CMD AssignResources (6)
  Given the subarray 001 is in the EMPTY state
  When the AssignResources command is sent to the subarray 001
  Then the subarray 001 should transition to the RESOURCING state
  Then the subarray 001 should transition to the IDLE state
  Then the central node reports a longRunningCommand successful completion

Scenario: RESOURCING to ABORTING - CMD Abort (12)
  Given the subarray 001 is in the RESOURCING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state

Scenario: IDLE to CONFIGURING - CMD Configure (16)
  Given the subarray 001 is in the IDLE state
  When the Configure command is sent to the subarray 001
  Then the subarray 001 should transition to the CONFIGURING state
  Then the subarray 001 should transition to the READY state


Scenario: IDLE to RESOURCING - CMD ReleaseResources (17)
  Given the subarray 001 is in the IDLE state
  When the ReleaseResources command is sent to the subarray 001
  Then the subarray 001 should transition to the RESOURCING state

Scenario: IDLE to RESOURCING - CMD AssignResources (18)
  Given the subarray 001 is in the IDLE state
  When the AssignResources command is sent to the subarray 001
  Then the subarray 001 should transition to the RESOURCING state

Scenario: IDLE to ABORTING - CMD Abort (19)
  Given the subarray 001 is in the IDLE state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state

Scenario: CONFIGURING to ABORTING - CMD Abort (25)
  Given the subarray 001 is in the CONFIGURING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state

Scenario: READY to SCANNING - CMD Scan (26)
  Given the subarray 001 is in the READY state
  When the Scan command is sent to the subarray 001
  Then the subarray 001 should transition to the SCANNING state

Scenario: READY to IDLE - CMD End (27)
  Given the subarray 001 is in the READY state
  When the End command is sent to the subarray 001
  Then the subarray 001 should transition to the IDLE state

Scenario: READY to ABORTING - CMD Abort (28)
  Given the subarray 001 is in the READY state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state

Scenario: READY to CONFIGURING - CMD Configure (29)
  Given the subarray 001 is in the READY state
  When the Configure command is sent to the subarray 001
  Then the subarray 001 should transition to the CONFIGURING state

Scenario: SCANNING to READY - CMD EndScan (32)
  Given the subarray 001 is in the SCANNING state
  When the EndScan command is sent to the subarray 001
  Then the subarray 001 should transition to the READY state

Scenario: SCANNING to ABORTING - CMD Abort (34)
  Given the subarray 001 is in the SCANNING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state

Scenario: ABORTED to RESTARTING - CMD Restart (40)
  Given the subarray 001 is in the ABORTED state
  When the Restart command is sent to the subarray 001
  Then the subarray 001 should transition to the RESTARTING state

Scenario: OBS_FAULT to RESTARTING - CMD Restart (46)
  Given the subarray 001 is in the OBS_FAULT state
  When the Restart command is sent to the subarray 001
  Then the subarray 001 should transition to the RESTARTING state