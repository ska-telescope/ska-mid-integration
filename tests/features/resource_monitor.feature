Feature: Resource Monitor updates
  Validate that the ResourceMonitor accurately updates dishesData after the 
  SubarrayNode assigns and releases resources

  @XTP-94112 @XTP-28347 @
  Scenario: Check ResourceMonitor updates after resource assignment and release
    Given the TMC and ResourceMonitor devices are ON
    And the subarray has assigned resources and is in IDLE obsState
    When the ResourceMonitor dishesData attribute should reflect the assigned resources
    Then all assigned resources are released
    And the ResourceMonitor dishesData attribute should reflect the updated state after resource release