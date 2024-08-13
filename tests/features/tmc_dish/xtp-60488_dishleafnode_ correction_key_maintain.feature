@XTP-60488 @tmc_mid @team_himalaya
Scenario Outline: Configure the telescope having TMC and Dish Subsystems with correction key
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And the TMC subarray is in IDLE obsState
    When I issue the Configure command to the TMC subarray with correction key <correction_key> 
    Then the DishMaster <dish_ids> transitions to dishMode OPERATE and pointingState TRACK
    And TMC subarray <subarray_id> obsState transitions to READY obsState

    Examples:
      | subarray_id | correction_key | dish_ids                         |
      | 1           | MAINTAIN       | SKA001,SKA036,SKA063,SKA100      |