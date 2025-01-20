Feature: Default

	
@XTP-70666 @XTP-73592 @XTP-28347 @Team_SAHYADRI
Scenario: Verify error propogation with defective dish
	Given the telescope is in ON state
	And TMC subarray is in ObsState IDLE
	When Dish 1 is set defective with <defect>
	And I issue the Configure command to the TMC subarray
	Then Exception <exception_message> is propagated to TMC subarray on longRunningCommandResult
	Examples:
	| defect                       | exception_message               | 
	| ERROR_PROPAGATION_DEFECT     | DISH_ERROR_MESSAGE              |