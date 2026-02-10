Feature: Automatic Stowing Functionality on DishLeafNode Devices

    Scenario: TMC validates SetStowMode command on DishLeafNode
        Given a DishLeafNode device in STANDBY_LP mode
        When I invoke the SetStowMode command on the DishLeafNode
        Then the dish transitions to STOW mode
        And the longRunningCommandResult event confirms command completion

