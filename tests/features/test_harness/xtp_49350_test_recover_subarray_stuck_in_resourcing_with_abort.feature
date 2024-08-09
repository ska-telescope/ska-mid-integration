@XTP-49344 @SKA_mid @Team_SAHYADRI
Scenario: TMC behavior when subarray stuck in obsState RESOURCING
    Given the telescope is in ON state
    And TMC subarray <subarray_id> busy in assigning resources
    And SDP subarray is defective and stuck in RESOURCING
    And CSP subarray transitioned to obsState IDLE
    And TMC subarray <subarray_id> stuck in obsState RESOURCING
    When I invoked Abort on TMC subarray <subarray_id>
    Then the CSP subarray and SDP subarray transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |