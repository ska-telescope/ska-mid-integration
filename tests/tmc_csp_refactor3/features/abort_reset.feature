# Feature: subarray 001 obsState may be Aborted and Restarted
This feature covers the call of the Abort command from all
the states that permit it and the subsequent call of the Reset command.

The purpose of these scenarios is to verify that the subarray obsState
can be successfully aborted and restarted from any state, ensuring so
that a tear down procedure to reset the subarray to a known EMPTY state is
feasible.

The states that permit the Abort command are:
- RESOURCING
- IDLE
- CONFIGURING
- READY
- SCANNING

The Abort command is expected to transition the subarray to the ABORTING.

After the subarray is in the ABORTING state, the subsequent expected
transition is the automatic transition to the ABORTED state. After that, 
the Restarted command can be called, and it will transition the subarray 
to the RESTARTING state, and then to the EMPTY state.

Background:
  Given the telescope is in ON state
  Given the subarray 001 can be used

Scenario: RESOURCING to ABORTING to ABORTED - CMD Abort (12)
  Given the subarray 001 is in the RESOURCING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state
  Then the subarray 001 should transition to the ABORTED state

Scenario: IDLE to ABORTING to ABORTED - CMD Abort (19)
  Given the subarray 001 is in the IDLE state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state
  Then the subarray 001 should transition to the ABORTED state

Scenario: CONFIGURING to ABORTING to ABORTED - CMD Abort (25)
  Given the subarray 001 is in the CONFIGURING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state
  Then the subarray 001 should transition to the ABORTED state

Scenario: READY to ABORTING to ABORTED - CMD Abort (28)
  Given the subarray 001 is in the READY state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state
  Then the subarray 001 should transition to the ABORTED state

Scenario: SCANNING to ABORTING to ABORTED - CMD Abort (34)
  Given the subarray 001 is in the SCANNING state
  When the Abort command is sent to the subarray 001
  Then the subarray 001 should transition to the ABORTING state
  Then the subarray 001 should transition to the ABORTED state

Scenario: ABORTED to RESTARTING - CMD Restart (40)
  Given the subarray 001 is in the ABORTED state
  When the Restart command is sent to the subarray 001
  Then the subarray 001 should transition to the RESTARTING state
  Then the subarray 001 should transition to the EMPTY state

