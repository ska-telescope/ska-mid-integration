Feature: Resource Monitor updates
  Validate that the ResourceMonitor accurately updates dishesData after the 
  SubarrayNode assigns and releases resources

  @XTP-94112 @XTP-28347 @
  Scenario: Check ResourceMonitor updates after resource assignment
    Given the TMC and ResourceMonitor devices are ON
    And the subarray has assigned resources and is in IDLE obsState
    Then the ResourceMonitor dishesData attribute should reflect the assigned resources
    When all assigned resources are released
    Then the ResourceMonitor dishesData attribute should reflect the updated state after resource release