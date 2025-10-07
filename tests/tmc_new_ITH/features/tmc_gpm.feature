Feature: Apply GPM configuration to dishes via TMC Mid Telescope

  Background:
    Given a TMC Mid telescope is operational

  Scenario Outline: TMC processes GPM JSON and reports status per dish
    Given the following GPM configurations are provided for version 1.0.0:
      | Dish_ID | Bands           |
      | SKA001  | Band_1, Band_5a |
      | SKA036  | Band_2          |
      | SKA093  | Band_5b         |
      | SKA063  | Band_3          |
    When the GPM configuration is applied via TMC
    Then TMC reports the status as below for the respective dish id:
      | Dish_ID | Status       | Reason                                |
      | SKA001  | GPM Applied  | Completed                             |
      | SKA036  | GPM Failed   | Dish is assigned to a subarray        |
      | SKA093  | GPM Failed   | Dish is not reachable                 |
      | SKA063  | GPM Failed   | Exception occurred during processing  |