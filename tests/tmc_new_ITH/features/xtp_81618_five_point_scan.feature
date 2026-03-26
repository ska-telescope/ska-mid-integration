@XTP-81618 @XTP-28347 @partial_configuration
Scenario Outline: TMC Behaviour when partial configuration is provided (similar case)
  Given a TMC
  And TMC SubarrayNode is in Ready ObsState
  When I execute partial configure command with <configuration_data>
  Then the TMC SubarrayNode transitions to obsState READY
  And provided configuration data applied on dish leaf node
  Examples:
   | configuration_data |
   | both_trajectory_ie_ce |
   | with_ie_ce |
   | with_trajectory |
