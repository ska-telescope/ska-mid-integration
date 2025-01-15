Feature: TMC SubarrayNode handles the failure when the Incremental AssignResources command fails on SDP Subarray
    @XTP-29014 @SKA_mid
    Scenario Outline: TMC behavior when SDP Subarray incremental AssignResources raises exception
        Given a TMC
        And AssignResources is executed with <input_json1> successfully on SubarrayNode <subarray_id>
        Given the next TMC SubarrayNode <subarray_id> AssignResources is in progress with <input_json2>
        And Sdp Subarray <subarray_id> raises exception and transitions to obsState FAULT
        And Csp Subarray <subarray_id> completes assign resources and transitions to obsState IDLE
        And the TMC SubarrayNode <subarray_id> stucks in RESOURCING
        When I issue the Abort command on TMC SubarrayNode <subarray_id>
        Then the SDP and TMC subarray <subarray_id> transitions to obsState FAULT and CSP transitions to obsState ABORTED
        When I issue the Restart command on TMC SubarrayNode <subarray_id>
        Then the CSP, SDP and TMC subarray <subarray_id> transitions to obsState EMPTY
        Then AssignResources command is executed successfully on the Subarray <subarray_id>

        Examples:
        | subarray_id  | input_json1                      | input_json2                                        |
        | 1            | incremental_assign_resources_01  | incremental_assign_invalid_resources_sdp_resources |