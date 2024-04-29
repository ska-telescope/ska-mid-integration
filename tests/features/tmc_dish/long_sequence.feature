Scenario: TMC executes long sequence of commands successfully
    Given a telescope in OFF or STANDBY state
    When I assign <resources> to TMC subarray <subarray_id>
    And I configure the subarray <subarray_id> with receiver_band_1
    And I issue End command to the subarray <subarray_id>
    Examples:
        | subarray_id | resources                             |
        | 1           | 'SKA001', 'SKA036', 'SKA063', 'SKA100' |