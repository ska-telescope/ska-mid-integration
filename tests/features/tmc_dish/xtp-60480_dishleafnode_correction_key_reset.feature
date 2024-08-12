@XTP-60480 @tmc_mid @team_himalaya
Scenario Outline: Configure the telescope having TMC and Dish Subsystems with correction key
    Given a Telescope consisting of TMC, DISH, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And the TMC subarray is in IDLE obsState
    When I issue the Configure command to the TMC subarray <subarray_id> with correction key <correction_key> 
    And the DishMaster transitions to dishMode OPERATE and pointingState TRACK
    And TMC subarray <subarray_id> obsState transitions to READY obsState

    Examples:
      | subarray_id | correction_key |
      | 1           | RESET         |