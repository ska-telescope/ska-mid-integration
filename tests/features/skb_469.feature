Feature: Default


@XTP-70071 @XTP-29778 @Team_SAHYADRI
Scenario: Verify SKB-469
	Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
	And the Telescope is in ON state
	And the subarray is in IDLE obsState
	And the command Configure is issued to the TMC subarray with <receiver_band1> and <scan_duration1> sec
	And the TMC subarray transitions to obsState READY
	And with command Scan TMC subarray transitions to obsState SCANNING
	And the TMC subarray transitions to obsState READY when scan duration <scan_duration1> is over
	And with command End TMC subarray transitions to obsState IDLE
	And with command ReleaseResources TMC subarray transitions to obsState EMPTY
	And with command AssignResources TMC subarray transitions to obsState IDLE
	When the command Configure is issued again to the TMC subarray with <receiver_band2> and <scan_duration2> sec
	Then the TMC subarray transitions to obsState READY
	And with command Scan TMC subarray transitions to obsState SCANNING
	And the TMC subarray transitions to obsState READY when scan duration <scan_duration2> is over
	And with command End TMC subarray transitions to obsState IDLE
	And with command ReleaseResources TMC subarray transitions to obsState EMPTY

		Examples:
		| receiver_band1 | scan_duration1 | receiver_band2 | scan_duration2 |       dish_ids                | 
		|       1        |      5         |       2        |      5         |   SKA001,SKA036,SKA063,SKA100 |