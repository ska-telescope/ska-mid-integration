@XTP-49354 @SKA_mid @Team_SAHYADRI
Scenario: Verify error propogation with failure on CSP Subarray while invoking AssignResources
    Given the telescope is in ON state
    When I issue the AssignResources to TMC while CSP subarray is set defective
    Then Exception is propagated to TMC on longRunningCommandResult