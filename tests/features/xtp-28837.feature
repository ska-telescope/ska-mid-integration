Feature: TMC SubarrayNode handles failure for Configure command    
    @SKA_mid @XTP-28837 @XTP-28347
    Scenario Outline: TMC behavior when CSP and SDP Subarray raises exception for Configure command
        Given a TMC
        And the resources are assigned to TMC SubarrayNode 
        And the TMC SubarrayNode <subarray_id> configure is in progress
        When Csp Subarray <subarray_id> raises exception and goes back to obsState IDLE
        And Sdp Subarray <subarray_id> raises exception and goes back to obsState IDLE
        Then Tmc SubarrayNode <subarray_id> aggregates and goes back to IDLE

        Examples:
        | subarray_id  |
        | 1            |