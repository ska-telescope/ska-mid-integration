@SKA_mid
Scenario Outline: Error Propagation Reported by TMC Mid Abort and Restart Commands for Defective Subarray
		Given the TMC subarray is in the IDLE observation state
		When Abort is invoked on a defectiveSubsystem <defectiveSubsystem>
		Then the TMC SubarrayNode obsstate changes to FAULT obsState
		Then the command failure is reported by subarray with error message with <defectiveSubsystem>
		Examples:
		        | defectiveSubsystem   |  
		        | CSP                  |  
		        | SDP                  |  