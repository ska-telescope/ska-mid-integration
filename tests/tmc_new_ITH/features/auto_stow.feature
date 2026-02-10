Feature: Automatic Stowing Functionality on DishLeafNode Devices

    Scenario: TMC validates SetStowMode command on DishLeafNode
        Given a DishLeafNode device in STANDBY_LP mode
        When I invoke the SetStowMode command on the DishLeafNode
        Then the dish transitions to STOW mode
        And the longRunningCommandResult event confirms command completion
    
    
    Scenario: Validate auto stow on gust speed
        Given a DishLeafNode device in STANDBY_FP mode
        When the gust speed is greater than the max allowed gust speed
        Then the dish automatically stows
    
    Scenario: Validate auto stow on mean wind speed exceed
        Given a DishLeafNode device in STANDBY_FP mode
        When the mean wind speed over a measurement time window exceeds the configured maximum threshold
        then the dish automatically stows



