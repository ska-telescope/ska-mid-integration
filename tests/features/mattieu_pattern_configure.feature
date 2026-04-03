@SKA_mid
    Scenario: TMC validates Mattieu Pattern Configure functionality
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command configure is issued with position velocity <input_json1>
        Then the subarray transitions to obsState READY
        And Dish Leaf Node Track Table Entries
        Examples:
        | input_json1 |
        | "mattieu_pattern_json"       |