@XTP-93827 @XTP-93825 @TEAM_HIMALAYA
Scenario: Verify array layout functionality in TMC mid
    Given the telescope is in ON state
    And AssignResources is invoked on the SubarrayNode with an arrayLayoutUri so that the SN.arrayLayoutUri attribute is updated
    When I invoke the Configure command on the SubarrayNode
    Then the DLN targetData attribute is updated using the array layout from Telmodel
    And CSP Subarray Leaf Node starts generating delay values with proper epoch
    And Program Track Table is populated correctly
    And TMC is able to memorize the array layout link on restart