@SKA_mid
Scenario Outline: Timeout reported by TMC Mid Abort command for subsystem subarray
		Given the TMC subarray is in the IDLE observation state
		When Abort is invoked on tmc with command timeout on <subsystem>
		Then the TMC SubarrayNode obsstate changes to FAULT obsState after timeout
		Then the command failure is reported by subarray with timeout error message with <subsystem>
		Examples:
		        | subsystem            |
		        | CSP                  |
		        | SDP                  |

@SKA_mid
Scenario Outline: Timeout reported by TMC Mid Restart command for subsystem subarray
		Given the TMC subarray is in the ABORTED observation state
		When Restart is invoked on tmc with command timeout on <subsystem>
		Then the TMC SubarrayNode obsstate stuck into RESTARTING obsState
		Then the command failure is reported by subarray with timeout error message with <subsystem>
		Examples:
		        | subsystem            |
		        | CSP                  |
		        | SDP                  |