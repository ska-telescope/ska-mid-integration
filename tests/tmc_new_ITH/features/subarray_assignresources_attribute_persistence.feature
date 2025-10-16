Feature: SubarrayNode AssignedResources attribute persistence after failed AssignResources

    As a TMC developer
    I want to ensure that the AssignedResources attribute maintains its state
    after a subsequent AssignResources command fails

    Scenario Outline: AssignedResources attribute persists after failed second AssignResources
        Given a TMC
        And AssignResources is executed successfully on SubarrayNode <subarray_id>
        And the AssignedResources attribute is updated with first assigned resources
        When I execute second AssignResources command on SubarrayNode <subarray_id> that fails
        Then the AssignedResources attribute should retain the first assigned resources
        And the subarray should remain in IDLE state

        Examples:
        | subarray_id  |
        | 1            |