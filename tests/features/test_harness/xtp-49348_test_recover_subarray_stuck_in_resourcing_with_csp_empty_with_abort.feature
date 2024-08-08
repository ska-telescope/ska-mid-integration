@XTP-49348 @SKA_mid @Team_SAHYADRI
Scenario: TMC behavior when subarray stuck in obsState RESOURCING
    Given Telescope is in on state
    And TMC subarray <subarray_id> busy in assigning resources
    And CSP subarray raised error goes back to obsState EMPTY
    And SDP subarray transitioned to obsState IDLE
    And TMC subarray <subarray_id> stuck in obsState RESOURCING
    When I invoked Abort on TMC subarray <subarray_id>
    Then the CSP subarray and SDP subarray transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |