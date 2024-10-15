Feature:  Invalid unexpected commands

    @XTP-29833
    Scenario: Unexpected commands not allowed when TMC subarray is empty
        Given the TMC is in ON state 
        And the subarray is in EMPTY obsstate
        When <unexpected_command> command is invoked, TMC raises exception
        Then TMC subarray remains in EMPTY obsstate
        And TMC executes the AssignResources command successfully
        Examples:
            | unexpected_command   |
            | Configure            |
            | Scan                 |
            | End                  |
            | Abort                |
            
    @XTP-29834
    Scenario: Unexpected commands not allowed when TMC subarray is idle
        Given the TMC is in ON state 
        And the subarray is in IDLE
        When <unexpected_command> command is invoked, TMC raises exception
        Then TMC subarray remains in IDLE obsState
        And TMC executes the <permitted_command> command successfully
        Examples:
            | unexpected_command  | permitted_command  |
            | Scan                |   Configure        |
            | Scan                |   ReleaseResources |

    @XTP-29835
    Scenario: Unexpected commands not allowed when TMC subarray is in Resourcing
        Given TMC is in ON state
        And the subarray is busy in assigning the resources
        When AssignResources command is invoked, TMC raises exception
        And previous AssignResources executed succesfully
        Then TMC executes the Configure command successfully   


    @XTP-29836
    Scenario: Unexpected commands not allowed when TMC subarray is READY
        Given the TMC is in ON state 
        And the subarray is in READY obsState
        When <unexpected_command> command is invoked, TMC raises exception
        Then TMC subarray remains in READY obsState
        And TMC executes the <permitted_command> command successfully
        Examples:
            | unexpected_command   | permitted_command |
            | AssignResources      | Configure         |
            | ReleaseResources     | Scan              |
            | EndScan              | End               |
            | EndScan              | Abort             |
            