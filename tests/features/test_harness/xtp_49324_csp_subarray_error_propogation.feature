Feature: Default

	
	@XTP-49324 @XTP-73592 @Team_SAHYADRI @SKA_mid
	Scenario: Verify error propogation with defective CSP Subarray
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		When CSP subarray is set defective
		And I issue the Configure command to the TMC subarray
		Then Exception is propagated to TMC subarray on longRunningCommandResult