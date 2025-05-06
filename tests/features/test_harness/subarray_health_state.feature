# This Feature cover scenario from excel sheet: https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=747888622
Scenario Outline: Subarray Health State should be Failed or Degraded when one or more devices health state is Failed or Degraded
Given csp subarray, sdp subarray and dish masters health state is OK 
When The <Devices> health state changes to <Device_Health_State> 
Then subarray health state is <Subarray_Health_State>
Examples:
    | Devices                                                 | Device_Health_State  | Subarray_Health_State |   
    | csp subarray                                            | FAILED               |  FAILED               | #Row 2
    | sdp subarray                                            | FAILED               |  FAILED               | #Row 3
    | csp subarray,sdp subarray                               | FAILED,FAILED        |  FAILED               | #Row 4
    | csp subarray                                            | DEGRADED             |  DEGRADED             | #Row 14
    | sdp subarray                                            | DEGRADED             |  DEGRADED             | #Row 15
    | csp subarray,sdp subarray                               | DEGRADED,DEGRADED    |  DEGRADED             | #Row 16
    | csp subarray,sdp subarray                               | DEGRADED,FAILED      |  FAILED               | #Row 22
    | csp subarray,sdp subarray                               | FAILED,DEGRADED      |  FAILED               | #Row 21
    | csp subarray,sdp subarray                               | UNKNOWN,DEGRADED     |  DEGRADED             | #Row 24

@XTP-33866 @XTP-73574 @Team_SAHYADRI
	Scenario Outline: Subarray Health State Changes based on Simulator Device Health State
		Given csp subarray, sdp subarray health state is OK
		And Dishes are assigned to Subarray with Health State as OK
		When  The <Devices> health state changes to <Device_Health_State>
		Then subarray health state is <Subarray_Health_State>
		Examples:
		    | Devices                                                 | Device_Health_State                      | Subarray_Health_State |   
		    | dish master 1                                           | FAILED                                   |  DEGRADED             | #Row 17
		    | dish master 2                                           | DEGRADED                                 |  DEGRADED             | #Row 18
		    | csp subarray,sdp subarray,dish master 1,dish master 2   | DEGRADED,DEGRADED,DEGRADED,DEGRADED      |  FAILED               | #Row 19 
		    | sdp subarray,dish master 1,dish master 2                | DEGRADED,DEGRADED,DEGRADED               |  FAILED               | #Row 20
		    | csp subarray,sdp subarray,dish master 1                 | DEGRADED,UNKNOWN,UNKNOWN                 |  DEGRADED             | 
		    | dish master 1,dish master 2                             | FAILED,FAILED                            |  FAILED               | #Row 5
		    | csp subarray,sdp subarray,dish master 1,dish master 2   | FAILED,FAILED,FAILED,FAILED              |  FAILED               | #Row 6
		    | csp subarray,dish master 1,dish master 2                | FAILED,FAILED,FAILED                     |  FAILED               | #Row 7
		    | csp subarray,sdp subarray,dish master 1                 | FAILED,DEGRADED,FAILED                   |  FAILED               | #Row 22
		
		    | csp subarray                                            | UNKNOWN                                  |  UNKNOWN              | #Row 10
		    | sdp subarray                                            | UNKNOWN                                  |  UNKNOWN              | #Row 9
		    | csp subarray,sdp subarray                               | UNKNOWN,UNKNOWN                          |  UNKNOWN              | #Row 8 
		    | dish master 1                                           | UNKNOWN                                  |  UNKNOWN              | #Row 12
		    | csp subarray,sdp subarray,dish master 1,dish master 2   | UNKNOWN,UNKNOWN,UNKNOWN,UNKNOWN          |  UNKNOWN              | #Row 11
		    | csp subarray,dish master 2                              | UNKNOWN,UNKNOWN                          |  UNKNOWN              | #Row 13

