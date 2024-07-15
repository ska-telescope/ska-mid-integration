# This BDD test performs TMC-Dish pairwise testing to verify long sequence of commands.
<<<<<<< HEAD
<<<<<<< HEAD
@XTP-42658 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: TMC executes long sequence of commands successfully
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    And TMC subarray is in IDLE obsState
<<<<<<< HEAD
    When I configure the subarray <subarray_id> with <receiver_band_1>
    And I issue End command to the subarray <subarray_id>
    And I reconfigure subarray <subarray_id> with <receiver_band_2>
    And I issue scan command with <scan_id> on subarray
    Then tmc subarraynode reports SCANNING obsState
    Examples:
        | subarray_id | dish_ids                     | scan_id | receiver_band_1 | receiver_band_2 |
        | 1           | SKA001,SKA036,SKA063,SKA100  |    1    |        1        |        2        |  
=======
@XTP-42658  @XTP-29778 @Team_SAHYADRI @tmc_dish
=======
@XTP-42658 @XTP-29778 @Team_SAHYADRI @tmc_dish
>>>>>>> 4399fb08 (SAH-1536: disable test case)
Scenario: TMC executes long sequence of commands successfully
    Given a telescope in OFF or STANDBY state
=======
>>>>>>> 7e55e6e5 (SAH-1536: Update test case for xtp-42658)
    When I assign <resources> to TMC subarray <subarray_id>
=======
    When I assign <dish_ids> to TMC subarray <subarray_id>
>>>>>>> b1798e1b (SAH-1536: Fix test case for xtp-42658)
=======
    And TMC subarray is in IDLE obsState
>>>>>>> 4a3d3a1e (SAH-1536: Add test case for tmc-dish unavailability)
    And I configure the subarray <subarray_id> with receiver_band_1
=======
    When I configure the subarray <subarray_id> with receiver_band_1
>>>>>>> f73b56f9 (SAH-1536: Code cleanup)
    And I issue End command to the subarray <subarray_id>
    And I reconfigure subarray <subarray_id> with receiver_band 2
    And I issue scan command with <scan_id> on subarray
    Then tmc subarraynode reports SCANNING obsState
    Examples:
<<<<<<< HEAD
<<<<<<< HEAD
        | subarray_id | resources                             | scan_id |
        | 1           | 'SKA001', 'SKA036', 'SKA063', 'SKA100' | 1      |
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
        | subarray_id | resources                                | scan_id |
        | 1           | ('SKA001', 'SKA036', 'SKA063', 'SKA100') | 1      |
>>>>>>> 90b9ee02 (SAH-1536: Update test case.)
=======
        | subarray_id | dish_ids                     | scan_id |
        | 1           | SKA001,SKA036,SKA063,SKA100  |    1    |
>>>>>>> b1798e1b (SAH-1536: Fix test case for xtp-42658)
