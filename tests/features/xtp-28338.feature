Feature: TMC SubarrayNode handles the failure when the AssignResources command fails on SDP Subarray    
    @XTP-28338 @XTP-28347 @SKA_mid
    Scenario Outline: TMC behavior when SDP Subarray AssignResources raises exception
        Given a TMC 
        And the TMC SubarrayNode <subarray_id> assign resources is in progress
        And Csp Subarray <subarray_id> completes assignResources
        And Sdp Subarray <subarray_id> raises exception and returns to obsState EMPTY
        And the TMC SubarrayNode <subarray_id> stucks in RESOURCING
        When I issue the command ReleaseAllResources on CSP Subarray <subarray_id>
        Then the CSP subarray <subarray_id> transitions to obsState EMPTY
        And Tmc SubarrayNode <subarray_id> transitions to obsState EMPTY
        And AssignResources command is executed successfully on the Subarray <subarray_id>

        Examples:
        | subarray_id  |
        | 1            |