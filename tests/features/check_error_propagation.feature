@SKA_mid @XTP-73592 @XTP-76068 @XTP-28347
Scenario Outline: Error Propagation Reported by TMC Mid End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a defectiveSubsystem <defectiveSubsystem>
		Then the command failure is reported by subarray with error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem   |
		            |READY            | END     | CSP                  |
		            |SCANNING         | ENDSCAN | CSP                  |
		            |READY            | SCAN    | CSP                  |
		            |READY            | END     | SDP                  |
		            |SCANNING         | ENDSCAN | SDP                  |
		            |READY            | SCAN    | SDP                  |
		            |READY            | END     | DISH                 |
		            |SCANNING         | ENDSCAN | DISH                 |
		            |READY            | SCAN    | DISH                 |


@SKA_mid @XTP-73592 @XTP-76069 @XTP-28347
	Scenario Outline: TimeOut Reported by TMC Mid End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a <defectiveSubsystem> Subarray
		Then the command failure is reported by subarray with appropriate error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem   |
		            |READY            | END     | CSP                  |
		            |SCANNING         | ENDSCAN | CSP                  |
		            |READY            | SCAN    | CSP                  |
		            |READY            | END     | SDP                  |
		            |SCANNING         | ENDSCAN | SDP                  |
		            |READY            | SCAN    | SDP                  |
		            |SCANNING         | ENDSCAN | DISH                 |
		            |READY            | SCAN    | DISH                 |
		            |READY            | END     | DISH                 |