#This test covers scenarios of Restart command flow when Configure command fails and TMC Subarray transitions to FAULT observation state.
@XTP-82860 @XTP-82747 @TEAM_HIMALAYA
Scenario Outline: Test Restart Command during failure of Configure Command
    Given CSP, SDP and DISH in <csp_obsstate>,<sdp_obsstate>,<dish_pointingstate> and <dish_dishmode> after <command>
    And TMC Subarray in observation state FAULT
    When I invoke Restart Command on the TMC Subarray
    Then CSP and SDP transitions to observation state EMPTY
    And Dish transitions to dishMode StandbyFP and PointingState READY
    And TMC subarray transitions to observation state EMPTY
    Examples:
        | command         | csp_obsstate | sdp_obsstate     | dish_pointingstate | dish_dishmode |
        | Configure       | FAULT        | READY            | READY              | CONFIG        |
        | Configure       | FAULT        | READY            | TRACK              | OPERATE       |
        | Configure       | FAULT        | READY            | SLEW               | OPERATE       |
        | Configure       | FAULT        | READY            | TRACK              | CONFIG        |
        | Configure       | FAULT        | READY            | READY              | OPERATE       |
        | Configure       | FAULT        | CONFIGURING      | READY              | CONFIG        |
        | Configure       | FAULT        | CONFIGURING      | TRACK              | OPERATE       |
        | Configure       | FAULT        | CONFIGURING      | SLEW               | OPERATE       |
        | Configure       | FAULT        | CONFIGURING      | TRACK              | CONFIG        |
        | Configure       | FAULT        | CONFIGURING      | READY              | OPERATE       |
        | Configure       | READY        | FAULT            | READY              | CONFIG        |
        | Configure       | READY        | FAULT            | TRACK              | OPERATE       |
        | Configure       | READY        | FAULT            | SLEW               | OPERATE       |
        | Configure       | READY        | FAULT            | TRACK              | CONFIG        |
        | Configure       | READY        | FAULT            | READY              | OPERATE       |
        | Configure       | CONFIGURING  | FAULT            | READY              | CONFIG        |
        | Configure       | CONFIGURING  | FAULT            | TRACK              | OPERATE       |
        | Configure       | CONFIGURING  | FAULT            | SLEW               | OPERATE       |
        | Configure       | CONFIGURING  | FAULT            | TRACK              | CONFIG        |
        | Configure       | CONFIGURING  | FAULT            | READY              | OPERATE       |
        | Configure       | CONFIGURING  | READY            | READY              | OPERATE       |
        | Configure       | CONFIGURING  | READY            | READY              | CONFIG        |
        | Configure       | CONFIGURING  | READY            | TRACK              | OPERATE       |
        | Configure       | CONFIGURING  | READY            | SLEW               | OPERATE       |
        | Configure       | CONFIGURING  | READY            | TRACK              | CONFIG        |
        | Configure       | CONFIGURING  | CONFIGURING      | READY              | CONFIG        |
        | Configure       | CONFIGURING  | CONFIGURING      | TRACK              | OPERATE       |
        | Configure       | CONFIGURING  | CONFIGURING      | SLEW               | OPERATE       |
        | Configure       | CONFIGURING  | CONFIGURING      | TRACK              | CONFIG        |
        | Configure       | CONFIGURING  | CONFIGURING      | READY              | OPERATE       |
        | Configure       | READY        | CONFIGURING      | READY              | CONFIG        |
        | Configure       | READY        | CONFIGURING      | TRACK              | OPERATE       |
        | Configure       | READY        | CONFIGURING      | SLEW               | OPERATE       |
        | Configure       | READY        | CONFIGURING      | TRACK              | CONFIG        |
        | Configure       | READY        | CONFIGURING      | READY              | OPERATE       |
        | Configure       | READY        | READY            | READY              | CONFIG        |
        | Configure       | READY        | READY            | READY              | OPERATE       |
        | End             | FAULT        | IDLE             | READY              | OPERATE       |
        | End             | IDLE         | FAULT            | READY              | OPERATE       |
        | End             | IDLE         | IDLE             | TRACK              | OPERATE       |
        | End             | IDLE         | FAULT            | TRACK              | OPERATE       |
        | End             | FAULT        | FAULT            | READY              | OPERATE       |
        | End             | FAULT        | IDLE             | TRACK              | OPERATE       |