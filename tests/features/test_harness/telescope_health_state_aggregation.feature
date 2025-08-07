# This Feature cover scenario from excel sheet: https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=825874621
@XTP-85070 @XTP-28347 @XTP-73574
Scenario Outline: Verify CentralNode TelescopeHealthState
    Given csp master, sdp master and dish masters health state is OK 
    When The <devices> health state changes to <health_state> 
    Then the telescope health state is <telescope_health_state>
    Examples:
        | devices                       | health_state               | telescope_health_state |   
        | csp master                    | FAILED                     |   FAILED               |  
        | sdp master                    | FAILED                     |   FAILED               |
        | csp master,sdp master         | FAILED,FAILED              |   FAILED               |
        | dish master 1                 | FAILED                     |   FAILED               | 
        | dish master 2                 | FAILED                     |   FAILED               |  
        | dish master 1,dish master 2   | FAILED,FAILED              |   FAILED               |  
        | csp master,dish master 1      | FAILED,FAILED              |   FAILED               |
        | csp master,dish master 2      | FAILED,FAILED              |   FAILED               |
        | sdp master,dish master 1      | FAILED,FAILED              |   FAILED               |  
        | sdp master,dish master 2      | FAILED,FAILED              |   FAILED               |

        | csp master                    | DEGRADED                   |   DEGRADED             |  
        | sdp master                    | DEGRADED                   |   DEGRADED             |
        | csp master,sdp master         | DEGRADED,DEGRADED          |   DEGRADED             |
        | dish master 1                 | DEGRADED                   |   DEGRADED             | 
        | dish master 2                 | DEGRADED                   |   DEGRADED             |   
        | dish master 1,dish master 2   | DEGRADED,DEGRADED          |   DEGRADED             |  
        | csp master,dish master 1      | DEGRADED,DEGRADED          |   DEGRADED             |
        | csp master,dish master 2      | DEGRADED,DEGRADED          |   DEGRADED             |
        | sdp master,dish master 1      | DEGRADED,DEGRADED          |   DEGRADED             |  
        | sdp master,dish master 2      | DEGRADED,DEGRADED          |   DEGRADED             | 
         
        | csp master                    | UNKNOWN                    |   UNKNOWN              |  
        | sdp master                    | UNKNOWN                    |   UNKNOWN              |
        | csp master,sdp master         | UNKNOWN,UNKNOWN            |   UNKNOWN              |
        | dish master 1                 | UNKNOWN                    |   UNKNOWN              | 
        | dish master 2                 | UNKNOWN                    |   UNKNOWN              |   
        | dish master 1,dish master 2   | UNKNOWN,UNKNOWN            |   UNKNOWN              |  
        | csp master,dish master 1      | UNKNOWN,UNKNOWN            |   UNKNOWN              |
        | csp master,dish master 2      | UNKNOWN,UNKNOWN            |   UNKNOWN              |
        | sdp master,dish master 1      | UNKNOWN,UNKNOWN            |   UNKNOWN              |  
        | sdp master,dish master 2      | UNKNOWN,UNKNOWN            |   UNKNOWN              |  

