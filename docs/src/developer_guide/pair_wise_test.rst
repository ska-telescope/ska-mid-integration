######################################
TMC MID integration Testing guidelines
######################################

****************************
Pair wise testing / Real-CSP
****************************

Pair wise testing is way of testing the TMC code with real CSP subsystem in place. 
using latest `test harness` implementation. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_csp execute the command `make k8s-test MARK=tmc-csp CSP_SIMULATION_ENABLED=false`.

* ``ON`` -               Testing On command on TMC with Real-CSP in place.
    
* ``Off`` - Testing Off command on TMC  with Real-CSP in place.

* ``AssignResources`` -  Testing AssignResources command on TMC with Real-CSP in place.

* ``Configure`` -  Testing Configure command on TMC with Real-CSP in place.

* ``Scan`` -  Testing Scan command on TMC with Real-CSP in place.

* ``EndScan`` -  Testing EndScan command on TMC with Real-CSP in place.

* ``End`` -  Testing End command on TMC with Real-CSP in place.
    
* ``ReleaseResources`` - Testing ReleaseResources command on TMC with Real-CSP in place.

* ``Standby`` -  Testing StandBy command on TMC with Real-CSP in place.

* ``Abort``    -  Testing Abort command on TMC with Real-CSP in place.

* ``Restart``   -  Testing Restart command on TMC with Real-CSP in place.



