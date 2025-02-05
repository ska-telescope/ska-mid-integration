@XTP-49365 @XTP-73592 @Team_SAHYADRI
Scenario: Verify error propogation with defective CSP Subarray on ReleaseResources
	Given the telescope is in ON state
	And TMC subarray is in ObsState IDLE
	When CSP subarray is set defective
	And I issue the ReleaseResources command to the TMC
	Then Exception is propagated to TMC on longRunningCommandResult