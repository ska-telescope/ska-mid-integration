Feature: Default

	
	@XTP-49327 @Team_SAHYADRI @configure
	Scenario: Verify timeout error propogation with defective SDP Subarray
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		When SDP subarray is set defective with timeout
		And I issue the Configure command to the TMC subarray
		Then Exception is propagated to TMC subarray on longRunningCommandResult