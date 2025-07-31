#This test covers scenarios of Restart command flow when Configure command fails and TMC Subarray transitions to FAULT observation state.
@XTP-82860 @XTP-82747 @TEAM_HIMALAYA
Scenario Outline: Test Restart Command during failure of Configure Command
    Given CSP, SDP and DISH in <csp_obsstate>,<sdp_obsstate>,<dish_pointingstates> and <dish_dishmode> after <command>
    And TMC Subarray in observation state FAULT
    When I invoke Restart Command on the TMC Subarray
    Then CSP and SDP transitions to observation state EMPTY
    And Dish transitions to dishMode StandbyFP and PointingState READY
    And TMC subarray transitions to observation state EMPTY
    Examples:
        | command         | csp_obsstate | sdp_obsstate     | dish_pointingstates     | dish_dishmode |
        | Configure       | FAULT        | READY            | READY,TRACK,TRACK,READY | CONFIG        |
        | Configure       | FAULT        | READY            | READY,READY,READY,READY | OPERATE       |
        | Configure       | FAULT        | READY            | SLEW,READY,SLEW,READY   | OPERATE       |