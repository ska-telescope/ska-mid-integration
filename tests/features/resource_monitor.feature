Feature: Resource Monitor updates
  Verify that the Resource Monitor device reflects changes to assigned resources
  when the SubarrayNode updates its assignedResources attribute.

  @SKA_mid
  Scenario: Verify ResourceMonitor updates when SubarrayNode assigned resources change
    Given the TMC and ResourceMonitor devices are ON
    And the subarray has assigned resources and is in IDLE obsState
    Then the ResourceMonitor dishesData attribute should reflect the assigned resources