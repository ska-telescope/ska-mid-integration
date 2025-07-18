######################################
TMC MID integration Testing guidelines
######################################

****************************
Pair wise testing - TMC-DISH
****************************

Pair wise testing is way of testing the TMC code with real DISH subsystem in place. 
using latest `test-harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_sdp pair execute the command `make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false`.

* ``On``                              -  Testing On command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.
    
* ``Off``                             -  Testing Off command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.
     
* ``Configure``                       -  Testing Configure command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``End``                             -  Testing End command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``Abort``                           -  Testing Abort command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``Scan``                            -  Testing Scan command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.
  
* ``Endscan``                         -  Testing Endscan command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``Successive Configure``            - Testing Successive Configure command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``Successive Scan``                 - Testing Successive Scan command on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``Long Sequence Commands``          - Testing Long Sequence Functionality Commands on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.

* ``TelescopeHealthState transition`` - Testing TelescopeHealthState transition on TMC with real DISH Masters and mocked/simulated SDP and CSP subsystems.
  

  