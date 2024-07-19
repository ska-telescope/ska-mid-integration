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
  Given the subarray 001 is in the EMPTY state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state

Scenario: RESOURCING to IDLE - AUTO Assigned (10)
  Given the subarray 001 is in the RESOURCING state
  When the automatic Assigned event occurs on the subarray 001
  Then the subarray 001 should transition to the IDLE state

Scenario: RESOURCING to IDLE - AUTO Released (11)
  Given the subarray 001 is in the RESOURCING state
  When the automatic Released event occurs on the subarray 001
  Then the subarray 001 should transition to the IDLE state

Scenario: RESOURCING to EMPTY - AUTO All released (13)
  Given the subarray 001 is in the RESOURCING state
  When the automatic All released event occurs on the subarray 001
  Then the subarray 001 should transition to the EMPTY state

Scenario: RESOURCING to OBS_FAULT - AUTO Observation fault (14)
  Given the subarray 001 is in the RESOURCING state
  When the automatic Observation fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: IDLE to OBS_FAULT - AUTO Observation Fault (20)
  Given the subarray 001 is in the IDLE state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: CONFIGURING to READY - AUTO Ready (22)
  Given the subarray 001 is in the CONFIGURING state
  When the automatic Ready event occurs on the subarray 001
  Then the subarray 001 should transition to the READY state

Scenario: CONFIGURING to OBS_FAULT - AUTO Observation Fault (23)
  Given the subarray 001 is in the CONFIGURING state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: READY to OBS_FAULT - AUTO Observation Fault (30)
  Given the subarray 001 is in the READY state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state

Scenario: SCANNING to READY - AUTO ScanComplete (33)
  Given the subarray 001 is in the SCANNING state
  When the automatic ScanComplete event occurs on the subarray 001
  Then the subarray 001 should transition to the READY state

Scenario: SCANNING to OBS_FAULT - AUTO Observation Fault (35)
  Given the subarray 001 is in the SCANNING state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: ABORTING to ABORTED - AUTO Abort complete (37)
  Given the subarray 001 is in the ABORTING state
  When the automatic Abort complete event occurs on the subarray 001
  Then the subarray 001 should transition to the ABORTED state

Scenario: ABORTING to OBS_FAULT - AUTO Observation Fault (38)
  Given the subarray 001 is in the ABORTING state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: ABORTED to OBS_FAULT - AUTO Observation Fault (41)
  Given the subarray 001 is in the ABORTED state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: RESTARTING to EMPTY - AUTO Restart Complete (43)
  Given the subarray 001 is in the RESTARTING state
  When the automatic Restart Complete event occurs on the subarray 001
  Then the subarray 001 should transition to the EMPTY state

Scenario: RESTARTING to OBS_FAULT - AUTO Observation Fault (44)
  Given the subarray 001 is in the RESTARTING state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state


Scenario: OBS_FAULT to OBS_FAULT - AUTO Observation Fault (47)
  Given the subarray 001 is in the OBS_FAULT state
  When the automatic Observation Fault event occurs on the subarray 001
  Then the subarray 001 should transition to the OBS_FAULT state
