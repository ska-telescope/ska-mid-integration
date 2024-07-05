Scenario: Dish manager reports the error when one of the subsystem is unavailable
    Given a telescope in OFF or STANDBY state
    And the TMC subarray is in IDLE obsState
    When one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED
    And I configure the subarray <subarray_id>
    Then dish manager should throw the error and report to TMC
    And TMC should propagate the error to client
    And the TMC SubarrayNode <subarray_id> remains in ObsState CONFIGURING
    Examples:
        | subarray_id |
        | 1           |