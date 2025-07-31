Feature: TMC SubarrayNode handles failure for Configure command
    @SKA_mid @XTP-28834 @XTP-28347
    Scenario Outline: TMC behavior when Csp Subarray is stuck in obsState CONFIGURING
        Given a TMC
        And the resources are assigned to TMC SubarrayNode
        And the TMC SubarrayNode <subarray_id> Configure is in progress
        And Sdp Subarray <subarray_id> completes Configure
        And Csp Subarray <subarray_id> is stuck in obsState CONFIGURING
        And the TMC SubarrayNode <subarray_id> transitions to FAULT
        When I issue the Abort command on TMC SubarrayNode <subarray_id>
        When I issue the Restart command on TMC SubarrayNode <subarray_id>
        Then the SDP subarray <subarray_id> transitions to obsState EMPTY
        And the CSP subarray <subarray_id> transitions to obsState EMPTY
        And Tmc SubarrayNode <subarray_id> transitions to obsState EMPTY
        And Configure command is executed successfully on the Subarray <subarray_id>

        Examples:
        | subarray_id  |
        | 1            |