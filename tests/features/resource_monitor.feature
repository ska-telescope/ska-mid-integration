Feature: Resource Monitoring Updates
    Verify that the ResourceMonitor device reflects SubarrayNode assigned resource changes.

    Scenario: Test Resource Monitoring updates when SubarrayNode attributes change
        Given the MID TMC and ResourceMonitor devices are ON
        And the MID subarray is in IDLE obsState
        When a change is triggered in the SubarrayNode assigned resources
        Then the ResourceMonitoring stationsData attribute should reflect the change
