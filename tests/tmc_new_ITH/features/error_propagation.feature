@SKA_mid
Scenario Outline: Error Propagation Reported by TMC Mid Abort command for defective subsystem subarray
		Given the TMC subarray is in the READY observation state
		When Abort is invoked on a defective subsystem <defective_subsystem>
		Then the TMC SubarrayNode obsstate changes to FAULT obsState
		Then the command failure is reported by subarray with error message with <defective_subsystem>
		Examples:
		        | defective_subsystem   |
		        | CSP                  |
		        | SDP                  |
                | Dish                 |


@SKA_mid
Scenario Outline: Error Propagation Reported by TMC Mid Restart command for defective subsystem subarray
		Given the TMC subarray is in the ABORTED observation state
		When Restart is invoked on a defective subsystem <defective_subsystem>
		Then the TMC SubarrayNode obsstate stuck into RESTARTING obsState
		Then the command failure is reported by subarray with error message with <defective_subsystem>
		Examples:
		        | defective_subsystem   |
		        | CSP                  |
		        | SDP                  |