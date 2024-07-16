Feature: Subarray State Transitions

  This feature covers all valid state transitions for a subarray.
  Each scenario represents a single transition triggered by either
  an automatic event (AUTO) or a command (CMD).

Scenario: READY to SCANNING CMD Scan - 26
  Given the subarray <subarray_id> is in the READY state
  When the Scan command is sent to subarray <subarray_id>
  Then the subarray <subarray_id> should transition to the SCANNING state
  Examples:
      | subarray_id |
      | 1 |
