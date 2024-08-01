Feature: test subarray command triggered transitions

  This feature covers all valid state transitions for a subarray 1
  that are triggered by commands, excluding Abort, Restart and the operational
  states (On, Off, Standby).

  Each scenario covers one or more transitions triggered by a Tango
  command; each scenario covers transition from a quiescent state to
  the subsequent quiescent state (i.e. from the starting state to
  a transitional one, followed by the transition to the subsequent
  quiescent state).


  Relevant transitions (taken from list_of_transitions.text):

  @CoversTransition("obsstate", "6. EMPTY --> (CMD: AssignResources) --> RESOURCING")
  @Transition("17. IDLE --> (CMD: ReleaseResources) --> RESOURCING")
  @Transition("18. IDLE --> (CMD: AssignResources) --> RESOURCING")
  @Transition("10. RESOURCING --> (AUTO: Assigned) --> IDLE")
  @Transition("11. RESOURCING --> (AUTO: Released) --> IDLE")
  @Transition("13. RESOURCING --> (AUTO: All released) --> EMPTY")
  @Transition("26. READY --> (CMD: Scan) --> SCANNING")
  @Transition("33. SCANNING --> (AUTO: ScanComplete) --> READY")
  @Transition("32. SCANNING --> (CMD: EndScan) --> READY")
  @Transition("27. READY --> (CMD: End) --> IDLE")
  @Transition("16. IDLE --> (CMD: Configure) --> CONFIGURING")
  @Transition("29. READY --> (CMD: Configure) --> CONFIGURING")
  @Transition("22. CONFIGURING --> (AUTO: Ready) --> READY

  Background:
    Given the telescope is in ON state
    Given the subarray 1 can be used

  @Transition("6. EMPTY --> (CMD: AssignResources) --> RESOURCING")
  @Transition("10. RESOURCING --> (AUTO: Assigned) --> IDLE")
  Scenario: EMPTY to RESOURCING to IDLE - CMD AssignResources
    Given the subarray 1 is in the EMPTY state
    When the AssignResources command is sent to the subarray 1 and the Assigned event is induced
    Then the subarray 1 should transition to the RESOURCING state
    And the subarray 1 should transition to the IDLE state
    And the central node reports a longRunningCommand  successful completion

  @Transition("16. IDLE --> (CMD: Configure) --> CONFIGURING")
  @Transition("22. CONFIGURING --> (AUTO: Ready) --> READY")
  Scenario: IDLE to CONFIGURING to READY - CMD Configure
    Given the subarray 1 is in the IDLE state
    When the Configure command is sent to the subarray 1
    Then the subarray 1 should transition to the CONFIGURING state
    And the subarray 1 should transition to the READY state
    And the subarray 1 longRunningCommand should be terminated

  @Transition("18. IDLE --> (CMD: AssignResources) --> RESOURCING")
  @Transition("10. RESOURCING --> (AUTO: Assigned) --> IDLE")
  Scenario: IDLE to RESOURCING to IDLE - CMD AssignResources
    Given the subarray 1 is in the IDLE state
    When the AssignResources command is sent to the subarray 1 to assign additional resources
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the IDLE state
    Then the central node longRunningCommand should be terminated

  @Transition("17. IDLE --> (CMD: ReleaseResources) --> RESOURCING")
  @Transition("13. RESOURCING --> (AUTO: All released) --> EMPTY")
  Scenario: IDLE to RESOURCING to EMPTY - CMD ReleaseResources
    Given the subarray 1 is in the IDLE state
    When the ReleaseResources command is sent to the subarray 1 and the All released event is induced
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the EMPTY state
    Then the central node longRunningCommand should be terminated
    Then the subarray 1 should transition to the RESOURCING state
    Then the subarray 1 should transition to the EMPTY state

  @Transition("26. READY --> (CMD: Scan) --> SCANNING")
  @Transition("33. SCANNING --> (AUTO: ScanComplete) --> READY")
  Scenario: READY to SCANNING to READY- CMD Scan
    Given the subarray 1 is in the READY state
    When the Scan command is sent to the subarray 1
    Then the subarray 1 should transition to the SCANNING state
    Then the subarray 1 should transition to the READY state
    Then the subarray 1 longRunningCommand should be terminated

  @Transition("27. READY --> (CMD: End) --> IDLE")
  Scenario: READY to IDLE - CMD End
    Given the subarray 1 is in the READY state
    When the End command is sent to the subarray 1
    Then the subarray 1 should transition to the IDLE state

  @Transition("29. READY --> (CMD: Configure) --> CONFIGURING")
  @Transition("22. CONFIGURING --> (AUTO: Ready) --> READY")
  Scenario: READY to CONFIGURING to READY - CMD Configure (13)
    Given the subarray 1 is in the READY state
    When the Configure command is sent to the subarray 1
    Then the subarray 1 should transition to the CONFIGURING state
    Then the subarray 1 should transition to the READY state
    Then the subarray 1 longRunningCommand should be terminated

  @Transition("32. SCANNING --> (CMD: EndScan) --> READY")
  Scenario: SCANNING to READY - CMD End Scan (17)
    Given the subarray 1 is in the SCANNING state
    When the Endscan command is sent to the subarray 1
    Then the subarray 1 should transition to the READY state

