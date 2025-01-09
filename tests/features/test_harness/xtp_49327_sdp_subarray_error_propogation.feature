Feature: Default

	
	@XTP-49327 @XTP-73592 @Team_SAHYADRI @SKA_mid
	Scenario: Verify CommandNotAllowed error propogation with defective SDP Subarray
		Given the telescope is in ON state
		Given SDP subarray is set with command not allowed defect
		When I issue the AssignResources command from TMC CentralNode
		Then CommandNotAllowed exception is propagated to TMC CentralNode on longRunningCommandResult