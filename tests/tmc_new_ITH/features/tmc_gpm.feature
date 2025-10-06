Feature: Apply GPM configuration to dishes via TMC Mid Telescope

  Background:
    Given a TMC Mid telescope is operational

  Scenario Outline: TMC processes GPM JSON and reports status per dish
    Given a GPM JSON is provided with version <Version>
      | Dish ID   | Bands   |
      | <Dish ID> | <Bands> |
    When the GPM configuration is applied via TMC
    Then TMC should report the following status per dish:
      | Dish ID   | Status       | Reason    |
      | <Dish ID> | <Status>     | <Reason>  |

  Examples:
    | Version | Dish ID | Bands           | Status       | Reason                                |
    | 1.0.0   | SKA001  | Band_1, Band_5a | GPM Applied  | Completed                             |
    | 1.0.0   | SKA063  | Band_3          | GPM Failed   | Dish is assigned to a subarray        |
    | 1.0.0   | SKA093  | Band_5b         | GPM Failed   | Dish is not reachable                 |
    | 1.0.0   | SKA100  | Band_4          | GPM Failed   | Exception occurred during processing  |