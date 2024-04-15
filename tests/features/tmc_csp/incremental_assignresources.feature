Scenario: Validate second AssignResources command  after first successful AssignResources and ReleaseResources are executed
    Given the TMC and CSP subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to TMC subarray <subarray_id>
    Then TMC and CSP subarray <subarray_id> must be in EMPTY obsState
    When I invoke second AssignResources on TMC subarray <subarray_id>
    Then TMC and CSP subarray <subarray_id> transitions to IDLE obsState
    Examples:
        | subarray_id  |
        | 1            |

Scenario: Validate succesive AssignResources command
    Given TMC subarray <subarray_id> is in EMPTY ObsState
    When I invoke First AssignResources on TMC subarray <subarray_id> with <input_json1> having <receptors1> on TMC subarray <subarray_id>
    Then TMC and CSP subarray <subarray_id> must be in IDLE obsState
    When I invoke second AssignResources on TMC subarray <subarray_id> with <input_json1> having <receptors> on TMC subarray <subarray_id>
    Then CSP subarray <subarray_id> must be in IDLE ObsState
    and TMC subarray <subarray_id> must be in IDLE obsState
    Examples:
    | subarray_id |
    | 1           |