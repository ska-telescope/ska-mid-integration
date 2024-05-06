 @XTP-28347
Scenario: Verify generated delay epoch values are less than delay advance time
    Given the telescope is in ON state
    And TMC subarray <subarray_id> in ObsState IDLE
    When I configure the TMC subarray
    Then Once configured is invoked delay starting generatig without wait
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values without waiting
    Examples:
        | subarray_id |
        | 1           |