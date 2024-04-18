Scenario: TMC-CSP succesive configure functionality
    Given a TMC and CSP
    And a subarray <subarray_id> in the IDLE obsState
    When I invoke First Configure command on TMC subarray <subarray_id> with <input_json1>
    And the subarray <subarray_id> transitions to obsState READY
    And I invoke Second Configure command on TMC subarray <subarray_id> with <input_json2>
    Then the subarray <subarray_id> reconfigures changing its obsState to READY

    Examples:
        | subarray_id  | input_json1          |      input_json2      |
        | 1            | sdp_mid_configure1   |   sdp_mid_configure1  |