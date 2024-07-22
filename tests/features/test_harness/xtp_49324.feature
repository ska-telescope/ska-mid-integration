Feature: Default

	
	@XTP-49324 @Team_SAHYADRI
	Scenario: test_configure_timeout_and_error_propagation_csp
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		When CSP subarray is set defective with timeout
		And I issue the Configure command to the TMC subarray
		Then Timeout error is propagated to TMC subarray on longRunningCommandResult