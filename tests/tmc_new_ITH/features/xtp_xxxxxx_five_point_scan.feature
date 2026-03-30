Scenario Outline: TMC is able to execute 5 point scan
  Given a TMC
  And TMC SubarrayNode is in Ready ObsState
  When I execute partial configure command with <configuration_data>
  Then the TMC SubarrayNode transitions to obsState READY
  And provided configuration data applied on dish leaf node
  Examples:
   | configuration_data    |
   | both_trajectory_ie_ce |