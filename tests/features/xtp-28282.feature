Feature: TMC SubarrayNode handles the failure when the AssignResources command fails on CSP Subarray
    @XTP-28282 @XTP-28347 @SKA_mid
    Scenario Outline: TMC behavior when Csp Subarray is stuck in obsState RESOURCING
        Given a TMC
        And the TMC SubarrayNode <subarray_id> assign resources is in progress
        And Sdp Subarray <subarray_id> completes assignResources
        And Csp Subarray <subarray_id> is stuck in obsState RESOURCING
        And the TMC SubarrayNode <subarray_id> transitions to FAULT
        When I issue the Restart command on TMC SubarrayNode <subarray_id>
        Then the CSP, SDP and TMC subarray <subarray_id> transitions to obsState EMPTY
        And AssignResources command is executed successfully on the Subarray <subarray_id>

        Examples:
        | subarray_id  |
        | 1            |
