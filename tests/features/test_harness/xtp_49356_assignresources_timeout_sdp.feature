@XTP-49356 @XTP-73592 @SKA_mid @Team_SAHYADRI
Scenario: Verify error propogation with failure on SDP Subarray while invoking AssignResources
    Given the telescope is in ON state
    When I issue the AssignResources to TMC while SDP subarray is set defective
    Then Exception is propagated to TMC on longRunningCommandResult