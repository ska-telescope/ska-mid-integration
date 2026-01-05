#This test covers scenarios of Restart command flow when AssignResources/Scan Command fails and TMC Subarray transitions to FAULT observation state.
@XTP-82859 @XTP-82747 @TEAM_HIMALAYA
Scenario Outline: Test Restart Command during failure of AssignResources and Scan Command
    Given CSP and SDP in observation states <csp_obsstate> and <sdp_obsstate> after <command>
    And TMC Subarray in observation state FAULT
    When I invoke Restart Command on the TMC Subarray
    Then CSP and SDP subarrays transitions to observation state EMPTY
    And TMC subarray transitions to observation state EMPTY
    Examples:
        | command         | csp_obsstate | sdp_obsstate     |
        | AssignResources | IDLE         | FAULT            |
        | AssignResources | RESOURCING   | FAULT            |
        | AssignResources | RESOURCING   | IDLE             |
        | AssignResources | RESOURCING   | RESOURCING       |
        | AssignResources | IDLE         | RESOURCING       |
        | Scan            | SCANNING     | FAULT            |
        | Scan            | FAULT        | SCANNING         |
        | ReleaseResources| FAULT        | IDLE             |
        | ReleaseResources| IDLE         | FAULT            |
        | ReleaseResources| RESOURCING   | FAULT            |
        | ReleaseResources| RESOURCING   | RESOURCING       |
        | ReleaseResources| FAULT        | FAULT            |
        | ReleaseResources| FAULT        | RESOURCING       |
        | EndScan         | FAULT        | READY            |
        | EndScan         | READY        | FAULT            |
        | EndScan         | FAULT        | FAULT            |