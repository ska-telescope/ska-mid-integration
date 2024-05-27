	Scenario: TMC mid raises an alarm when it encounters NaN in received pointing calibration
		Given a TMC mid with already executed calibration scans
		When the Dish Leaf Node receives NaN number from SDP
		Then the alarm is raised for NaN found in last pointing data