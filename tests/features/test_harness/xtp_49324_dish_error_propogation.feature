Feature: Default

	
	@XTP-49324 @Team_SAHYADRI @SKA_mid
	Scenario: Verify error propogation with defective dish
		Given the telescope is in ON state
		And TMC subarray is in ObsState IDLE
		When Dish 1 is set defective
		And I issue the Configure command to the TMC subarray
		Then Exception is propagated to TMC subarray on longRunningCommandResult