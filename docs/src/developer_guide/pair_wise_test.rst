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

Long command sequence implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``TMC Mid executes configure-scan sequence of commands successfully`` - Testing TMC-CSP long sequence for configure-scan functionality by parameterizing the scan_types and scan_ids

*``TMC Mid executes multiple scan with same configuration successfully`` - Testing TMC-CSP long sequence for multiple scans functionality by parameterizing the scan_types and scan_ids

*``TMC Mid executes multiple scans with different resources and configurations`` - Testing TMC-CSP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids

*''TMC Mid executes multiple scans with different configurations, intermittently ending configurations'' - Testing TMC-CSP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids intermittently ending configurations

*''TMC-CSP succesive configure functionality''- Testing TMC-CSP long sequence for configure functionality by parameterizing the subarray_id and different configure_json
