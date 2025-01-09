@XTP-49344 @XTP-73592 @SKA_mid @Team_SAHYADRI
Scenario: TMC behavior when subarray stuck in obsState RESOURCING with defective SDP
    Given the telescope is in ON state
    And TMC subarray <subarray_id> busy in assigning resources
    And SDP subarray is defective and stuck in RESOURCING
    And CSP subarray transitioned to obsState IDLE
    And TMC subarray <subarray_id> stuck in obsState RESOURCING
    When I invoked Abort on TMC subarray <subarray_id>
    Then the CSP subarray transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |