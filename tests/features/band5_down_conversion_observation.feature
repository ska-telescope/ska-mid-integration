Feature:  TMC executes band 5 down conversion observation
    @SKA_mid @XTP-87827 @XTP-28347
    Scenario: TMC executes band 5 down conversion observation
        Given the TMC is On
        And the subarray is in IDLE obsState using <assign_json>
        When the command configure is issued with <configure_json> 
        Then the subarray transitions to obsState READY
        And the subarray executes scan


        Examples:
        | assign_json               | configure_json                      |
        | AssignResources_band5_dc  | Configure_band5_dc                  |
        | assign_resources_mid      | Configure_mid_v6_detected_filterbank|
        | assign_resources_mid      | Configure_mid_v6_pulsar_timing      |
        | assign_resources_mid      | Configure_mid_v6_voltage_recorder   |
        | assign_resources_mid      | Configure_mid_v6_flow_through       |