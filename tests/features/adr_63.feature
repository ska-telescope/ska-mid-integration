Feature: TMC able to Configure Subarray with ADR-63 based changes 
    @SKA_mid @XTP-75211
    Scenario Outline: TMC behavior when configure command is invoked with ADR-63 JSON
        Given a TMC
        When the resources are assigned to TMC SubarrayNode
        And the Configure command is invoked with respective ADR-63 changes input
        Then the TMC SubarrayNode transitions to obsState READY
