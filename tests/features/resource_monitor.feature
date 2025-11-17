Feature: Resource Monitor updates
  Validate that the ResourceMonitor accurately updates dishes after the 
  SubarrayNode assigns and releases resources

  @XTP-94112 @XTP-28347
  Scenario: Check ResourceMonitor updates after resource assignment and release
    Given the telescope is in ON state
    And the resources are assigned to the subarray <subarray_id> and is in IDLE obsState
    And the ResourceMonitor dishes attribute should reflect the assigned resources
    When all assigned resources are released
    Then the ResourceMonitor dishes attribute should reflect the updated state after resource release

    Examples:
    | subarray_id   |
    | 1             |