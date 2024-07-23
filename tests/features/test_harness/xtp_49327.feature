Feature: Default

	
	@XTP-49327 @Team_SAHYADRI
	Scenario: test_configure_timeout_and_error_propagation_sdp
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		When SDP subarray is set defective with timeout
		And I issue the Configure command to the TMC subarray
		Then Timeout error is propagated to TMC subarray on longRunningCommandResult