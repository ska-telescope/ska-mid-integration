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
        | command   | csp_obsstate | sdp_obsstate | dish_pointingstates     | dish_dishmode |
        | Configure | FAULT        | READY        | READY,TRACK,TRACK,READY | CONFIG        |
        | Configure | FAULT        | READY        | READY,READY,READY,READY | OPERATE       |
        | Configure | FAULT        | READY        | SLEW,READY,SLEW,READY   | OPERATE       |
        | Configure | FAULT        | READY        | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | FAULT        | READY        | READY,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | FAULT        | CONFIGURING  | TRACK,READY,TRACK,TRACK | CONFIG        |
        | Configure | FAULT        | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | FAULT        | CONFIGURING  | TRACK,SLEW,SLEW,TRACK   | OPERATE       |
        | Configure | FAULT        | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | FAULT        | CONFIGURING  | READY,TRACK,TRACK,READY | OPERATE       |
        | Configure | READY        | FAULT        | READY,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | READY        | FAULT        | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | READY        | FAULT        | SLEW,TRACK,TRACK,TRACK  | OPERATE       |
        | Configure | READY        | FAULT        | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | READY        | FAULT        | TRACK,READY,TRACK,TRACK | OPERATE       |
        | Configure | CONFIGURING  | FAULT        | TRACK,TRACK,READY,TRACK | CONFIG        |
        | Configure | CONFIGURING  | FAULT        | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | CONFIGURING  | FAULT        | TRACK,TRACK,SLEW,SLEW   | OPERATE       |
        | Configure | CONFIGURING  | FAULT        | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | CONFIGURING  | FAULT        | READY,TRACK,TRACK,READY | OPERATE       |
        | Configure | CONFIGURING  | READY        | TRACK,READY,READY,TRACK | OPERATE       |
        | Configure | CONFIGURING  | READY        | READY,READY,READY,READY | CONFIG        |
        | Configure | CONFIGURING  | READY        | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | CONFIGURING  | READY        | SLEW,SLEW,SLEW,SLEW     | OPERATE       |
        | Configure | CONFIGURING  | READY        | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | CONFIGURING  | CONFIGURING  | READY,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | CONFIGURING  | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | CONFIGURING  | CONFIGURING  | SLEW,TRACK,TRACK,TRACK  | OPERATE       |
        | Configure | CONFIGURING  | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | CONFIGURING  | CONFIGURING  | TRACK,READY,TRACK,TRACK | OPERATE       |
        | Configure | READY        | CONFIGURING  | TRACK,TRACK,READY,TRACK | CONFIG        |
        | Configure | READY        | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | READY        | CONFIGURING  | TRACK,TRACK,TRACK,SLEW  | OPERATE       |
        | Configure | READY        | CONFIGURING  | TRACK,TRACK,TRACK,TRACK | CONFIG        |
        | Configure | READY        | CONFIGURING  | READY,TRACK,TRACK,TRACK | OPERATE       |
        | Configure | READY        | READY        | READY,READY,TRACK,TRACK | CONFIG        |
        | Configure | READY        | READY        | READY,TRACK,TRACK,TRACK | OPERATE       |
        | End       | FAULT        | IDLE         | READY,READY,READY,READY | OPERATE       |
        | End       | IDLE         | FAULT        | READY,READY,READY,READY | OPERATE       |
        | End       | IDLE         | IDLE         | TRACK,READY,TRACK,TRACK | OPERATE       |
        | End       | IDLE         | FAULT        | TRACK,TRACK,TRACK,TRACK | OPERATE       |
        | End       | FAULT        | FAULT        | READY,READY,READY,READY | OPERATE       |
        | End       | FAULT        | IDLE         | READY,READY,READY,READY | OPERATE       |

