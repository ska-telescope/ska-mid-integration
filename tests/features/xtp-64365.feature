# This BDD test performs TMC-Dish pairwise testing to verify Abort command flow.
@Team_SAHYADRI @XTP-64365 @SKA_mid
Scenario: TMC mid executes Abort command on DISH with pointingState READY
    Given a Telescope consisting of TMC, DISH <dish_ids>
    And the Telescope is in ON state
    And TMC subarray <subarray_id> is in obsState READY
    And DishMaster <dish_ids> is in dishMode OPERATE with pointingState READY
    When I issue the Abort command to the TMC subarray <subarray_id>
    Then the Dish <dish_ids> transitions to dishMode STANDBY_FP and pointingState READY
    And TMC SubarrayNode transitions to obsState ABORTED
    Examples:

        | subarray_id | dish_ids                       |
        | 1           | SKA001,SKA036,SKA063,SKA100   |