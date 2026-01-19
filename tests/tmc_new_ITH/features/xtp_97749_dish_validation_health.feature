  @XTP-97748 @XTP-XTP-97749 @Team_HIMALAYA
  Scenario Outline: Dish validation failure impacts telescope health
    Given a TMC
    And Telescope is in ON state
    And I assign resources to TMC Subarray
    And Dish Leaf Node has "<validation_type>" validation condition
    When Dish Leaf Node health is evaluated
    Then Dish Leaf Node healthState shall be "<dln_health>"
    And TMC Subarray Node healthState shall be "<propagated_health>"
    And telescopeHealthState shall be "<propagated_health>"
    And an alarm shall be raised for "<validation_type>" validation failure

  Examples:
    | validation_type | dln_health | propagated_health |
    | all_ok          | OK         | OK                |
    | kvalue mismatch | FAILED     | DEGRADED          |
    | gpm mismatch    | DEGRADED   | DEGRADED          |