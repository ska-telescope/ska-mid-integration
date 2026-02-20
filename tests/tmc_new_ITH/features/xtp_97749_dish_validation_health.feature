  @XTP-97748 @XTP-97749 @Team_HIMALAYA
  Scenario Outline: Dish validation failure impacts telescope health
    Given a TMC
    And Telescope is in ON state
    And I assign resources to TMC Subarray
    When Dish Leaf Node has "<validation_type>" validation condition
    Then Dish Leaf Node healthState shall be "<dln_health>"
    And TMC Subarray Node healthState shall be "<propagated_health>"
    And telescopeHealthState shall be "<propagated_health>"
    And HealthInfo will be updated for "<validation_type>" 
    And an alarm shall be raised for "<validation_type>" validation failure

  Examples:
    | validation_type | dln_health | propagated_health |
    | kvalue mismatch | FAILED     | DEGRADED          |
    | gpm mismatch    | DEGRADED   | DEGRADED          |
    | all_ok          | OK         | OK                |