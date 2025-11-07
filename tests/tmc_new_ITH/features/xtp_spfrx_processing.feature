@XTP- @XTP-28347
Scenario Outline: TMC Behaviour when SPFRx configuration is provided
  Given a TMC
  And TMC SubarrayNode is in IDLE ObsState
  When I execute SPFRx configure command with <configuration_data>
  Then the TMC SubarrayNode transitions to obsState READY
  Examples:
   | configuration_data                                   |
   | configuration_with_all_dish                          |
   | configuration_with_single_parameter_per_dish         |
   | configuration_with_multiple_dish_same_parameter      |
   | configuration_with_all_different                     |
