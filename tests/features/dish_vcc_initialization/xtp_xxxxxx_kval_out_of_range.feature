Feature: TMC throws error when the kValue is out of range
    Scenario Outline: TMC is able to reject command when kValue is out of range 
        Given a TMC
        And Telescope is in ON state 
        When I issue the command LoadDishCfg on TMC with Dish and VCC configuration file   
        Then TMC rejects the command with error {error_message}
        Examples:
            | error_message |
            | K values are not in range (1 to 1177)|