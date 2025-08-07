Feature: TMC is able to load Dish and VCC map configuration file and display current version of file
    @XTP-28676 @XTP-28347
    Scenario Outline: TMC is able to load Dish and VCC configuration file  
        Given a TMC
        And Telescope is in ON state 
        When I issue the command LoadDishCfg on TMC with Dish and VCC configuration file   
        Then TMC should pass the configuration to CSP Controller
        And TMC should set Dish k-numbers provided in file on dish master devices
        And TMC displays the current version of Dish and VCC configuration 
