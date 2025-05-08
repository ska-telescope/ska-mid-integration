@SKA_mid
Scenario Outline: Error Propagation Reported by TMC Mid Abort and Restart Commands for Defective Subarray
		Given the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a defectiveSubsystem <defectiveSubsystem>
		Then the command failure is reported by subarray with error message
		Then the TMC SubarrayNode remains in <stuck> obsState
		Examples:
		            | initialObsState | command | defectiveSubsystem   |  stuck  |
		            | IDLE            | Abort   | CSP                  |  IDLE   |
		            # | IDLE            | Abort   | SDP                  |  IDLE   |
		            # | ABORTED         | Restart | CSP                  | ABORTED |
		            # | ABORTED         | Restart | SDP                  | ABORTED |