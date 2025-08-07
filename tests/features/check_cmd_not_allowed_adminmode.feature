	@XTP-84035 @XTP-84039 @XTP-28347 @TEAM_HIMALAYA
	Scenario: Command not allowed from CentralNode when subsystem adminmode is OFFLINE/NOT_FITTED
		Given the adminmode of subsystem controller <subsystem> is <adminmode>
		When I invoke command <command> on centralnode
		Then the centralnode rejects the command 
		Examples:
		| subsystem           | adminmode    | command          |
		| cspcontroller       | OFFLINE      | On               |
		| cspcontroller       | OFFLINE      | AssignResources  |
		| sdpcontroller       | NOT_FITTED   | AssignResources  |
		| sdpcontroller       | NOT_FITTED   | ReleaseResources |
		| sdpcontroller       | OFFLINE      | standby          |
		| sdpcontroller       | NOT_FITTED   | ReleaseResources |


	@XTP-84042 @XTP-84039 @XTP-28347 @TEAM_HIMALAYA
	Scenario: Command not allowed from SubarrayNode when subsystem adminmode is OFFLINE/NOT_FITTED
		Given the adminmode of subsystem subarray <subsystem> is <adminmode>
		When I invoke command <command> on subarraynode
		Then the subarraynode rejects the command
		Examples:
		| subsystem         | adminmode    | command   |
		| cspsubarray       | OFFLINE      | Configure |
		| cspsubarray       | NOT_FITTED   | Scan      |
		| sdpsubarray       | OFFLINE      | End       |
		| sdpsubarray       | NOT_FITTED   | EndScan   |
		
