@XTP-42757 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario Outline: Testing of successive Scan functionality for tmc-dish interface
    Given a Telescope in ON state and TMC subarray in IDLE obsState
    And the command Configure is issued to the TMC subarray with <receiver_band1> and <scan_duration1> sec
    And the TMC subarray transitions to obsState READY
    And with command Scan TMC subarray transitions to obsState SCANNING
    And the TMC subarray transitions to obsState READY when scan duration <scan_duration1> is over
    And with command End TMC subarray transitions to obsState IDLE
    When the next configure command is issued to the TMC subarray with <receiver_band2> and <scan_duration2> sec
    Then the TMC subarray transitions to obsState READY
    And with command Scan TMC subarray transitions to obsState SCANNING
    And the TMC subarray transitions to obsState READY when scan duration <scan_duration2> is over

        Examples:
        | receiver_band1 | scan_duration1 | receiver_band2 | scan_duration2 |
        |       1        |      300       |       2        |      500       |