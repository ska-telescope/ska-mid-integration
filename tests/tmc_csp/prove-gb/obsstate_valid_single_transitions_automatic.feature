# Feature: subarray 001 State Transitions - Event Triggered
This feature covers all valid automatic state transitions for a subarray,
focusing on events that trigger transitions without explicit commands.
Each scenario represents a single transition triggered by an automatic
event (AUTO).

The purpose of these scenarios is to verify that the subarray correctly
responds to various system events and conditions,
transitioning between states as expected without direct operator intervention.
This ensures the robustness and reliability of the subarray control system in
handling both normal operational flows and error conditions.

Key aspects tested include:
2. Resource allocation and release
3. Configuration and readiness states
4. Observation execution and completion
5. Error handling (Observation Faults)
6. Abort and restart procedures

These scenarios complement the command-triggered transitions,
providing comprehensive coverage of the subarray's state machine behavior.
They are crucial for validating the overall reliability, safety,
and autonomous capabilities of the telescope control system.


Background:
  Given the telescope is in ON state
  Given the subarray 001 can be used

Scenario: EMPTY to OBS_FAULT - AUTO Observation Fault (8)
  When the subarray 001 is in the EMPTY state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state

Scenario: RESOURCING to IDLE - AUTO Assigned (10)
  When the subarray 001 is in the RESOURCING state and the Assigned event is induced
  Then the subarray 001 should transition to the IDLE state

Scenario: RESOURCING to IDLE - AUTO Released (11)
  When the subarray 001 is in the RESOURCING state and the Released event is induced
  Then the subarray 001 should transition to the IDLE state

Scenario: RESOURCING to EMPTY - AUTO All released (13)
  When the subarray 001 is in the RESOURCING state and the All released event is induced
  Then the subarray 001 should transition to the EMPTY state

Scenario: RESOURCING to OBS_FAULT - AUTO Observation fault (14)
  When the subarray 001 is in the RESOURCING state  and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: IDLE to OBS_FAULT - AUTO Observation Fault (20)
  When the subarray 001 is in the IDLE state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: CONFIGURING to READY - AUTO Ready (22)
  When the subarray 001 is in the CONFIGURING state and the Ready event is induced
  Then the subarray 001 should transition to the READY state

Scenario: CONFIGURING to OBS_FAULT - AUTO Observation Fault (23)
  When the subarray 001 is in the CONFIGURING state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: READY to OBS_FAULT - AUTO Observation Fault (30)
  When the subarray 001 is in the READY state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state

Scenario: SCANNING to READY - AUTO ScanComplete (33)
  When the subarray 001 is in the SCANNING state and the ScanComplete event is induced
  Then the subarray 001 should transition to the READY state

Scenario: SCANNING to OBS_FAULT - AUTO Observation Fault (35)
  When the subarray 001 is in the SCANNING state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: ABORTING to ABORTED - AUTO Abort complete (37)
  When the subarray 001 is in the ABORTING state and the Abort complete event is induced
  Then the subarray 001 should transition to the ABORTED state

Scenario: ABORTING to OBS_FAULT - AUTO Observation Fault (38)
  When the subarray 001 is in the ABORTING state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: ABORTED to OBS_FAULT - AUTO Observation Fault (41)
  When the subarray 001 is in the ABORTED state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: RESTARTING to EMPTY - AUTO Restart Complete (43)
  When the subarray 001 is in the RESTARTING state and the Restart Complete event is induced
  Then the subarray 001 should transition to the EMPTY state

Scenario: RESTARTING to OBS_FAULT - AUTO Observation Fault (44)
  When the subarray 001 is in the RESTARTING state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: OBS_FAULT to OBS_FAULT - AUTO Observation Fault (47)
  When the subarray 001 is in the OBS_FAULT state and an observation fault occurs
  Then the subarray 001 should transition to the OBS_FAULT state
