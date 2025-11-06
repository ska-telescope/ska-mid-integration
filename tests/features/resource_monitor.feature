Feature: Resource Monitoring updates for MID
  This feature verifies that the ResourceMonitor device correctly updates its
  dishesData attribute when the SubarrayNode assigned resources change.

  Scenario: Test Resource Monitoring updates when SubarrayNode attributes change
    Given the MID TMC and ResourceMonitor devices are ON
    And the MID subarray is in IDLE obsState
    When the SubarrayNode assigned resources are modified
    Then the ResourceMonitoring dishesData attribute should reflect the change