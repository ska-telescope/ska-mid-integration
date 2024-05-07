 @XTP-28347
Scenario: Verify SKB-329
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is moved to ObsState IDLE
    When I configure the TMC subarray
    Then Once the TMC Subarray is configured, CspSubarrayLeafNode immediately starts generating delay polynomials
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values without waiting
    Examples:
        | subarray_id |
        | 1           |