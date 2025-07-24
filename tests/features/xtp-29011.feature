Feature: TMC SubarrayNode handles the failure when the Incremental AssignResources command fails on CSP and SDP Subarrays
    @XTP-29011 @XTP-28347 @SKA_mid
    Scenario Outline: TMC behavior when CSP and SDP Subarrays incremental AssignResources raise exception
        Given a TMC
        And AssignResources is executed successfully on SubarrayNode <subarray_id> with <input_json1>
        Given the next TMC SubarrayNode <subarray_id> AssignResources is in progress with <input_json2>
        And Csp Subarray <subarray_id> raises exception and returns to obsState IDLE
        And Sdp Subarray <subarray_id> raises exception and returns to obsState IDLE
        And the TMC SubarrayNode <subarray_id> stucks in RESOURCING
        When I issue the command ReleaseAllResources on SDP and CSP Subarray <subarray_id>
        Then Tmc SubarrayNode <subarray_id> transitions to obsState EMPTY
        Then AssignResources command is executed successfully on the Subarray <subarray_id>

       Examples:
       | subarray_id  | input_json1                      | input_json2                                         |
       | 1            | incremental_assign_resources_01  | incremental_assign_invalid_resources_sdp_resources  |