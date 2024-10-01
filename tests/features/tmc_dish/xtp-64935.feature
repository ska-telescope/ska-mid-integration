Feature:  TMC executes successive configure commands
    @tmc_dish
    Scenario: TMC validates reconfigure functionality with real dish
        Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
        And the Telescope is in ON state
        And the subarray is in IDLE obsState
        When the command configure is issued with <input_json1>
        Then the subarray transitions to obsState READY for <dish_ids>
        When the next successive configure command is issued with <input_json2>
        Then the subarray reconfigures changing its obsState to READY for <dish_ids>

        Examples:
            | input_json1           |      input_json2       | dish_ids |
            | multiple_configure1   |   multiple_configure2  |  SKA001,SKA036 |
            | multiple_configure1   |   multiple_configure1  | SKA001,SKA036  |