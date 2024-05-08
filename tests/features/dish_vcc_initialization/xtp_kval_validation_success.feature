Feature: TMC handles kValue validation	
    Scenario: TMC Validates the kValue when all kvalues are same
        Given a TMC
        And Telescope is in ON state 
        When I issue the command LoadDishCfg on TMC with all same kValue
        And TMC subarray in ObsState IDLE
        Then I successfully invoke Configure command on TMC


    Scenario: TMC Validates the kValue when all kvalues are different
        Given a TMC
        And Telescope is in ON state 
        When I issue the command LoadDishCfg on TMC with all different kValue
        And TMC subarray in ObsState IDLE
        Then I successfully invoke Configure command on TMC
