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
