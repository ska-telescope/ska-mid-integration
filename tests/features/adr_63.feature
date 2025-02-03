Feature: TMC able to Configure Subarray with ADR-63 based changes 
    @SKA_mid @XTP-75211
    Scenario Outline: TMC behavior when configure command is invoked with ADR-63 compliant JSON
        Given a TMC
        And the resources are assigned to TMC SubarrayNode
        And TMC behavior when configure command is invoked with ADR-63 JSON
        Then the TMC SubarrayNode transitions to obsState READY
