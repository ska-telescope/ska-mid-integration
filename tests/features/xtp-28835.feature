Feature: TMC SubarrayNode handles failure for Configure command    
    @SKA_mid @XTP-28835 @XTP-28347
    Scenario Outline: TMC behavior when SDP Subarray Configure raises exception
        Given a TMC
        And the resources are assigned to TMC SubarrayNode
        And the TMC SubarrayNode <subarray_id> Configure is in progress
        And Csp Subarray <subarray_id> completes Configure
        And Sdp Subarray <subarray_id> raises exception and goes back to obsState IDLE
        And the TMC SubarrayNode <subarray_id> stucks in CONFIGURING
        When I issue the Abort command on TMC SubarrayNode <subarray_id>
        Then the SDP subarray <subarray_id> transitions to obsState ABORTED
        And the CSP subarray <subarray_id> transitions to obsState ABORTED
        And Tmc SubarrayNode <subarray_id> transitions to obsState ABORTED
        When I issue the Restart command on TMC SubarrayNode <subarray_id>
        Then the SDP subarray <subarray_id> transitions to obsState EMPTY
        And the CSP subarray <subarray_id> transitions to obsState EMPTY
        And Tmc SubarrayNode <subarray_id> transitions to obsState EMPTY
        And Configure command is executed successfully on the Subarray <subarray_id>

        Examples:
        | subarray_id  |
        | 1            |
