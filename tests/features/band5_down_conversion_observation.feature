Feature:  TMC executes band 5 down conversion observation
    @SKA_mid @XTP-85071 @XTP-28347
    Scenario: TMC executes band 5 down conversion observation
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command configure is issued with band 5 dc configuration
        Then the subarray transitions to obsState READY
        And the subarray executes scan