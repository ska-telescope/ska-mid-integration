######################################
TMC MID integration Testing guidelines
######################################

***************************
Pair wise testing - TMC-SDP
***************************

Pair wise testing is way of testing the TMC code with real SDP subsystem in place. 
using latest `test-harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_sdp pair execute the command `make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false`.

* ``On``               -  Testing On command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.
    
* ``Off``              -  Testing Off command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``Standby``          -  Testing Standby command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``AssignResources``  -  Testing AssignResources command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.
    
* ``ReleaseResources`` -  Testing ReleaseResources command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.
    
* ``Configure``        -  Testing Configure command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``End``              -  Testing End command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``Scan``             -  Testing Scan command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``EndScan``          -  Testing EndScan command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``Abort``            -  Testing Abort command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

* ``Restart``          -  Testing Restart command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.

Negative Scenario implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``HealthState.DEGRADED Scenario`` - Testing TMC-SDP for the verification of the TelescopeHealthState transition in the Telescope Monitoring and 
    Control system based on the health state changes of the SDP Controller. 
    - The scenario simulates a telescope setup consisting of Real SDP, and simulated devices for the CSP and the Dish.

* ``SDP Component Unavailable`` - Testing TMC-SDP for the verification of whether the SDP component is available or not and it successfully reports the
    availability of the component to TMC.
Long command sequence implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``TMC Mid executes configure-scan sequence of commands successfully`` - Testing TMC-SDP long sequence for configure-scan functionality by parameterizing the scan_types and scan_ids

*``TMC Mid executes multiple scan with same configuration successfully`` - Testing TMC-SDP long sequence for multiple scans functionality by parameterizing the scan_types and scan_ids

*``TMC Mid executes multiple scans with different resources and configurations`` - Testing TMC-SDP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids
