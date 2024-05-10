 @XTP-28347
Scenario: Verify SKB-329
    Given the telescope is in ON state
    And TMC Subarray <subarray_id> is moved to obsState IDLE
    When I configure the TMC Subarray
    Then Once the TMC Subarray is configured, CspSubarrayLeafNode immediately starts generating delay polynomials
    Then the TMC Subarray <subarray_id> transitions to obsState READY
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values without waiting
    Examples:
        | subarray_id |
        | 1           |