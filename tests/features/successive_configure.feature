Feature:  TMC executes successive configure commands
    Scenario: TMC validates reconfigure functionality
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command configure is issued with <input_json1>
        Then the subarray transitions to obsState READY
        When the next successive configure command is issued with <input_json2>
        Then the subarray reconfigures changing its obsState to READY
        And test goes for the tear down
        Examples:
            | input_json1           |      input_json2       |
            | multiple_configure1   |   multiple_configure2  |
            | multiple_configure1   |   multiple_configure1  |