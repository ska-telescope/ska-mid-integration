Feature: SubarrayNode AssignedResources attribute persistence after failed AssignResources

    As a TMC developer
    I want to ensure that the AssignedResources attribute maintains its state
    after a subsequent AssignResources command fails
    @XTP-92537 @XTP-28347 @TEAM_SAHYADRI
    Scenario Outline: AssignedResources attribute persists after failed second AssignResources
        Given a TMC
        And AssignResources is executed successfully with <receptor1> on SubarrayNode <subarray_id>
        And the AssignedResources attribute is updated with first assigned resources <receptor1>
        When second AssignResources with receptor <receptor2> on SubarrayNode <subarray_id> fails
        Then the AssignedResources attribute should retain the first assigned resources <receptor1>
        And the subarray should move to observation FAULT

        Examples:
        | subarray_id  | receptor1  | receptor2  |
        | 1            | SKA001     | SKA036     |