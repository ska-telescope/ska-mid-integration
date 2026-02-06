Feature: Apply STOW mode to dishes via TMC Mid Telescope

  Background:
    Given a TMC Mid telescope is operational

  Scenario: TMC processes SetStowMode command and reports status per dish
    Given the following dish ids are provided as input to the SetStowMode command:
      | Dish_ID |
      | SKA001  |
      | SKA036  |
      | SKA063  |
      | SKA100  |
      | SKA019  |
    When the SetStowMode command is invoked via TMC
    Then TMC reports the status as below for the respective dish id:
      | Dish_ID | Status                       | Reason                            |
      | SKA001  | DishMode set to Stow         | SetStowMode successfully executed |
      | SKA100  | DishMode set to Stow         | SetStowMode successfully executed |
      | SKA036  | DishMode set to Stow         | Dish is already in stow mode      |
      | SKA019  | Dish is unreachable          | Dish is not allocated to TMC      |
      | SKA063  | Exception occurred           | Issue in the respective dish      |
