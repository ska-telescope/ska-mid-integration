@XTP-49344 @XTP-28347 @Team_SAHYADRI
Scenario: TMC behavior when subarray stuck in obsState FAULT
    Given the telescope is in ON state
    And TMC subarray <subarray_id> busy in assigning resources
    And SDP subarray raised error goes back to obsState EMPTY
    And CSP subarray transitioned to obsState IDLE
    And TMC subarray <subarray_id> stuck in obsState FAULT
    When I invoked Abort on TMC subarray <subarray_id>
    Then the CSP subarray transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |