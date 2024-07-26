Feature: subarray 1 State Transitions - Command Triggered

This feature covers all valid state transitions for a subarray 1,
focusing only on command-triggered transitions.
Each scenario represents a transition triggered by a command (CMD)
from a quiescent state and up to a quiescent state, possibly
passing through intermediate transient states or
a transition that can only start from an internal event (like observation fault)

Operational states are also excluded.

There are 26 scenarios.

Background:
  Given the telescope is in ON state
  Given the subarray 1 can be used


Scenario: EMPTY to RESOURCING to IDLE - CMD AssignResources (1)
  Given the subarray 1 is in the EMPTY state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the IDLE state

Scenario: RESOURCING to ABORTING to ABORTED - CMD Abort (2)
  Given the subarray 1 is in the RESOURCING state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should transition to the ABORTING state
  Then the subarray 1 should transition to the ABORTED state

Scenario: IDLE to CONFIGURING to READY - CMD Configure (3)
  Given the subarray 1 is in the IDLE state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should transition to the CONFIGURING state

Scenario: IDLE to RESOURCING to IDLE - CMD ReleaseResources (4)
  Given the subarray 1 is in the IDLE state
  When the ReleaseResources command is sent to the subarray 1 and the Released event is induced
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the IDLE state

Scenario: IDLE to RESOURCING to EMPTY - CMD ReleaseResources (5)
  Given the subarray 1 is in the IDLE state
  When the ReleaseResources command is sent to the subarray 1  and the All released event is induced
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the EMPTY state

Scenario: IDLE to RESOURCING to IDLE - CMD AssignResources (6)
  Given the subarray 1 is in the IDLE state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the IDLE state


Scenario: EMPTY to RESOURCING to IDLE - CMD AssignResources (16)
  Given the subarray 1 is in the IDLE state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should transition to the RESOURCING state
  Then the subarray 1 should transition to the IDLE state

Scenario: IDLE to ABORTING to ABORTED - CMD Abort (7)
  Given the subarray 1 is in the IDLE state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should transition to the ABORTING state
  Then the subarray 1 should transition to the ABORTED state

Scenario: CONFIGURING to ABORTING to ABORTED - CMD Abort (8)
  Given the subarray 1 is in the CONFIGURING state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should transition to the ABORTING state
  Then the subarray 1 should transition to the ABORTED state

Scenario: READY to SCANNING to READY- CMD Scan (9)
  Given the subarray 1 is in the READY state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should transition to the SCANNING state
  Then the subarray 1 should transition to the READY state

Scenario: READY to IDLE - CMD End (10)
  Given the subarray 1 is in the READY state
  When the End command is sent to the subarray 1
  Then the subarray 1 should transition to the IDLE state

Scenario: READY to ABORTING to ABORTED - CMD Abort (11)
  Given the subarray 1 is in the READY state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should transition to the ABORTING state
  Then the subarray 1 should transition to the ABORTED state


Scenario: SCANNING to ABORTING to ABORTED - CMD Abort (12)
  Given the subarray 1 is in the SCANNING state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should transition to the ABORTING state
  Then the subarray 1 should transition to the ABORTED state

Scenario: READY to CONFIGURING to READY - CMD Configure (13)
  Given the subarray 1 is in the READY state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should transition to the CONFIGURING state
  Then the subarray 1 should transition to the READY state

Scenario: ABORTED to RESTARTING to EMPTY - CMD Restart (14)
  Given the subarray 1 is in the ABORTED state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should transition to the RESTARTING state
  Then the subarray 1 should transition to the EMPTY state

Scenario: OBS_FAULT to RESTARTING to EMPTY - CMD Restart (15)
  Given the subarray 1 is in the OBS_FAULT state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should transition to the RESTARTING state
  Then the subarray 1 should transition to the EMPTY state

Scenario: SCANNING to READY - CMD End Scan (17)
  Given the subarray 1 is in the SCANNING state
  When the Endscan command is sent to the subarray 1
  Then the subarray 1 should transition to the READY state




Scenario: EMPTY to OBS_FAULT - AUTO Observation Fault (20)
  When the subarray 1 is in the EMPTY state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state


Scenario: RESOURCING to OBS_FAULT - AUTO Observation fault (21)
  When the subarray 1 is in the RESOURCING state  and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state


Scenario: IDLE to OBS_FAULT - AUTO Observation Fault (22)
  When the subarray 1 is in the IDLE state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state

Scenario: CONFIGURING to OBS_FAULT - AUTO Observation Fault (23)
  When the subarray 1 is in the CONFIGURING state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state


Scenario: READY to OBS_FAULT - AUTO Observation Fault (24)
  When the subarray 1 is in the READY state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state
#
Scenario: SCANNING to OBS_FAULT - AUTO Observation Fault (25)
  When the subarray 1 is in the SCANNING state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state


Scenario: ABORTING to OBS_FAULT - AUTO Observation Fault (26)
  When the subarray 1 is in the ABORTING state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state

Scenario: ABORTED to OBS_FAULT - AUTO Observation Fault (27)
  When the subarray 1 is in the ABORTED state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state

Scenario: RESTARTING to OBS_FAULT - AUTO Observation Fault (28)
  When the subarray 1 is in the RESTARTING state and an observation fault occurs
  Then the subarray 1 should transition to the OBS_FAULT state