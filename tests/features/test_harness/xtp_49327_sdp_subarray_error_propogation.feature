Feature: Default

	
	@XTP-49327 @Team_SAHYADRI @configure
	Scenario: Verify CommandNotAllowed error propogation with defective SDP Subarray
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		And SDP subarray is set with command not allowed defect
		When I issue the Configure command from TMC SubarrayNode
		Then CommandNotAllowed exception is propagated to TMC SubarrayNode on longRunningCommandResult