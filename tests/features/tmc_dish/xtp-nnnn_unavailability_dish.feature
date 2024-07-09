Scenario: Dish manager reports the error when one of the subsystem is unavailable
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray is in IDLE obsState
    When one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED
    And I configure the subarray <subarray_id>
<<<<<<< HEAD
    Examples:
        | subarray_id |
        | 1           |
=======
    Then dish manager should throw the error and report to TMC
    And TMC should propagate the error to client
    And the TMC SubarrayNode <subarray_id> remains in ObsState CONFIGURING
    
        Examples:
        | subarray_id  | dish_ids                       |
        | 1            | SKA001,SKA036,SKA063,SKA100    |
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
=======
    Given a telescope in ON state
=======
    Given a telescope in OFF or STANDBY state
>>>>>>> 1de465a4 (SAH-1536: Update test case)
    And the TMC subarray is in IDLE obsState
=======
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray is in IDLE obsState
>>>>>>> bfcbd823 (SAH-1536: Add test case for tmc-dish unavailability)
    When one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED
    And I configure the subarray <subarray_id>
<<<<<<< HEAD
    Examples:
        | subarray_id |
        | 1           |
<<<<<<< HEAD
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
=======
    Then dish manager should throw the error and report to TMC
    And TMC should propagate the error to client
    And the TMC SubarrayNode <subarray_id> remains in ObsState CONFIGURING
    
        Examples:
        | subarray_id  | dish_ids                       |
        | 1            | SKA001,SKA036,SKA063,SKA100    |
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
>>>>>>> bfcbd823 (SAH-1536: Add test case for tmc-dish unavailability)
