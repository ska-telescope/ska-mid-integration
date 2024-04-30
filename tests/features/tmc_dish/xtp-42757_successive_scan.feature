@XTP-42757 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario Outline: Testing of successive Scan functionality for tmc-dish interface
    Given a Telescope in ON state and TMC subarray in IDLE obsState
    And the command Configure is issued to the TMC subarray with <receiver_band> and <scan_duration> sec
    And the TMC subarray transitions to obsState READY
    And with command Scan TMC subarray transitions to obsState SCANNING
    And the TMC subarray transitions to obsState READY when scan duration <scan_duration> is over
    And with command End TMC subarray transitions to obsState IDLE
    When the next configure command is issued to the TMC subarray with <receiver_band> and <scan_duration> sec
    Then the TMC subarray transitions to obsState READY
    And with command Scan TMC subarray transitions to obsState SCANNING
    And the TMC subarray transitions to obsState READY when scan duration <scan_duration> is over

        Examples:
        | receiver_band | scan_duration |
        |       1       |      300      |
        |       2       |      500      |