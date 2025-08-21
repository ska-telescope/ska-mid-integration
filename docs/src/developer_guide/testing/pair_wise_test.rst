.. _pairwise_testing:

====================================
TMC Mid pair wise Testing guidelines
====================================

.. note::
    Update as of June 2025: From PI 24 onwards the pairwise testing has been 
    moved from this repository to SKA Mid Software Integration repository. 
    Currently, in that repo too, the pairwise testing is disabled by default. 
    It is still possible to perform pair wise testing with certain settings 
    and modifications. This article is kept here to maintain the knowledge 
    base.


TMC - SDP Pair
===============

Pair wise testing is way of testing the TMC code with real SDP subsystem in place. 
using latest `test harness` implemented. 

Commands implemented
--------------------
To test with tmc_sdp execute the command::

    make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false

* ``ON`` - Testing On command on TMC with Real-SDP in place.
* ``Off`` - Testing Off command on TMC  with Real-SDP in place.
* ``AssignResources`` -  Testing AssignResources command on TMC with Real-SDP in place.
* ``ReleaseResources``- Testing ReleaseResources command on TMC with Real-SDP in place.
* ``Standby`` - Testing StandBy command on TMC with Real-SDP in place.
* ``Configure``- Testing Configure command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.
* ``End`` - Testing End command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Dish subsystems.
* ``Scan`` - Testing Scan command on TMC with Real-SDP in place.
* ``EndScan`` - Testing EndScan command on TMC with Real-SDP in place.
* ``Abort`` - Testing Abort command on TMC with Real-SDP in place.
* ``Restart`` - Testing Restart command TMC with Real-SDP in place.

Negative Scenario implemented
--------------------------------

* ``HealthState.DEGRADED Scenario``
        - Testing TMC-SDP to verification of the TelescopeHealthState transition.
        - In the Telescope Monitoring and Control TMC system based on the health state changes of the SDP Controller. 
        - The scenario simulates a telescope setup consisting of real SDP, and simulated devices for the CSP and the Dish.
* ``SDP Component Unavailable`` - Testing TMC-SDP for the verification of whether the SDP component is available or not and it successfully reports the availability of the component to TMC.

Long command sequence implementation
--------------------------------------

* ``TMC Mid executes configure-scan sequence of commands successfully`` - Testing TMC-SDP long sequence for configure-scan functionality by parameterizing the scan_types and scan_ids
* ``TMC Mid executes multiple scans with same configuration successfully`` - Testing TMC-SDP long sequence for multiple scans functionality by parameterizing the scan_types and scan_ids
* ``TMC Mid executes multiple scans with different resources and configurations``- Testing TMC-SDP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids

TMC - CSP Pair
==============

Pair wise testing is way of testing the TMC code with real CSP subsystem in place. 
using latest `test harness` implemented. 

Commands implemented
--------------------
To test with tmc_csp execute the command::

    `make k8s-test MARK=tmc_csp CSP_SIMULATION_ENABLED=false`

* ``ON`` - Testing On command on TMC with Real-CSP in place.
* ``Standby`` - Testing Standby command on TMC with Real-CSP in place.
* ``AssignResources`` - Testing AssignResources command on TMC with Real-CSP in place.
* ``ReleaseResources``- Testing ReleaseResources command on TMC with Real-CSP in place.
* ``Configure``- Testing Configure command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``End`` - Testing End command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``Scan``- Testing Scan command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``EndScan`` - Testing EndScan command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``Abort`` - Testing Abort command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``Restart`` - Testing Restart command on TMC with real CSP controller and CSP Subarrays and simulated SDP and Dish subsystems.
* ``LoadDishCfg`` - Testing LoadDishCfg command on TMC with real CSP controller simulated SDP and Dish subsystems.

Long command sequence implementation
--------------------------------------

* ``TMC Mid executes configure-scan sequence of commands successfully`` - Testing TMC-CSP long sequence for configure-scan functionality by parameterizing the scan_types and scan_ids
* ``TMC Mid executes multiple scans with same configuration successfully`` - Testing TMC-CSP long sequence for multiple scans functionality by parameterizing the scan_types and scan_ids
* ``TMC Mid executes multiple scans with different resources and configurations``- Testing TMC-CSP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids

TMC - Dish Pair
===============

To test with tmc_sdp pair execute the command `make k8s-test MARK=tmc_dish DISH_SIMULATION_ENABLED=false`.

Commands implemented
--------------------

* ``SetStandbyLPMode``
* ``SetStandbyFPMode``
* ``SetStandbyOperateMode``
* ``ConfigureBand``
* ``Track``
* ``TrackStop``
* ``Abort``
* ``LoadDishCfg``