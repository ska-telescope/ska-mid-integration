Feature:  TMC executes successive configure commands
    @tmc_dish
    Scenario: TMC validates reconfigure functionality with real dish
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command configure is issued with <input_json1>
        Then the subarray transitions to obsState READY
        When the next successive configure command is issued with <input_json2>
        Then the subarray reconfigures changing its obsState to READY

        Examples:
            | input_json1           |      input_json2       |
            | multiple_configure1   |   multiple_configure2  |
            | multiple_configure1   |   multiple_configure1  |