@XTP-81402 @XTP-28347 @TEAM_HIMALAYA
Scenario Outline: TMC behavior when configure command is invoked with wrap_sector
    Given a TMC
    When the resources are assigned to TMC SubarrayNode
    And I execute configure json <configure_json> <conf_type> with wrap_sector <wrap_sector>
    Then the TMC SubarrayNode transitions to obsState READY
    And provided <wrap_sector> is applied on dish leaf node
    Examples:
    | configure_json               | wrap_sector | conf_type         |
    | configure_mid                | 0           | deprecated        |
    | configure_adr_63             | -1          | with_receptors    |
    | configure_adr_63             | 0           | without_receptors |
    | configure_holography_adr106  | -1          | adr_106           |  