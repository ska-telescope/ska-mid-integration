Scenario: Dish manager reports the error when one of the subsystem is unavailable
    Given a telescope in OFF or STANDBY state
    And the TMC subarray is in IDLE obsState
    When one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED
    And I configure the subarray <subarray_id>
    Examples:
        | subarray_id |
        | 1           |