@XTP-93827 @XTP-93825 @TEAM_HIMALAYA
Scenario: Verify array layout functionality in TMC mid
    Given the telescope is in ON state
    And AssignResources is invoked on the SubarrayNode with an arrayLayoutUri so that the SN.arrayLayoutUri attribute is updated
    When I invoke the Configure command on the SubarrayNode
    Then the DLN targetData attribute is updated using the array layout referenced by SN.arrayLayoutUri
    #And the Dish receives the layout data and generates the corresponding PTT configuration
    #And the DPD targetData attribute reflects the correct processed layout data
    #And the delay calculation module uses the updated layout information to compute and publish the delay values