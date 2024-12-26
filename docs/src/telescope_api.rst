MID Telescope Deployment
=========================

MID Telescope deployment comes with the following components:

1. **TMC** 

2. **SDP-LMC**

3. **CSP-LMC**

4. **MCCS-LMC**

Configurable Options
---------------------

* a. **instances** : Users can provide the array of device server deployment instances required for a component.

    Default for components are:

    #. **TMC** : ["01"] 

    #. **SDP-LMC** : ["01"] 

    #. **CSP-LMC** : ["01"]

    #. **MCCS-LMC** : ["01"]

* b. **subarray_count** : Users can set the subarray count according to the number of device server deployment instances required for a component.

    Default Value is 2.
    
    #. **TMC** 

    #. **SDP-LMC** 

    #. **CSP-LMC** 

    #. **MCCS-LMC** 

* c. **file** : Users can provide a custom device server configuration file to the components. Default is `configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-mid-integration/-/blob/main/charts/ska-tmc-mid/data/>`_

* d. **enabled** : Users can opt to disable any component by setting this value to False. Default is True for all components.

* e. **tmc_subarray_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of TMC Subarray.

* f. **csp_subarray_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of CSP-LMC Subarray.

* g. **sdp_subarray_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of SDP-LMC Subarray.

* h. **csp_master_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of CSP-LMC Master.

* i. **sdp_master_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of SDP-LMC Master.

* j. **csp_subarray_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of CSP Subarray.

* k. **sdp_subarray_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of SDP Subarray.

* l. **csp_master** : This value is present under global settings. Users can use this to change the FQDN of CSP-LMC Master.

* m. **sdp_master** : This value is present under global settings. Users can use this to change the FQDN of SDP-LMC Master.

* n. **mccs_master** : This value is present under global settings. Users can use this to change the FQDN of MCCS-LMC Master.

* o. **mccs_master_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of MCCS-LMC Master.

* p. **mccs_subarray_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of MCCS Subarray.

* q. **mccs_subarray_ln_prefix** : This value is present under global settings. Users can use this to change the FQDN prefix of MCCS Subarray Leaf Node.

* r. **DelayCadence** : This refers to the time difference (in seconds) between each publication of delay values to the `delayModel` attribute on the CSP-LMC Subarray.

* s. **DelayValidityPeriod** : This represents the duration (in seconds) for which delay values remain valid after being published.

* t. **DelayModelTimeInAdvance** : This indicates the time in seconds by which delay values need to be available in advance.

* u. **CspAssignResourcesInterfaceURL** : Interface version for CSP assign resources command. 
                                    This value is present under Subarray Node. Currently defaults to "https://schema.skao.int/tmc-mid-csp-assignresources/3.0"

* v. **CspScanInterfaceURL** : Interface version for CSP scan command. 
                                    This value is present under Subarray Node. Currently defaults to "https://schema.skao.int/tmc-mid-csp-scan/2.0"

* w **SdpScanInterfaceURL**: Interface version for SDP scan command. 
                                    This value is present under Subarray Node. Currently defaults to "https://schema.skao.int/ska-sdp-scan/0.4"

* x **MccsConfigureInterfaceURL**: Interface version for MCCS configure command. 
                                    This value is present under Subarray Node. Currently defaults to "https://schema.skao.int/tmc-mid-mccs-configure/1.0"

* y **MccsScanInterfaceURL**: Interface version for MCCS scan command. 
                                    This value is present under Subarray Node. Currently defaults to "https://schema.skao.int/tmc-mid-mccs-scan/3.0"


MID Telescope Sub-system FQDNs:
--------------------------------
Below are the FQDNs of the MID Telescope components. For updated FQDNs, kindly refer to `values.yaml` in the Low Telescope charts.

+------------------------------------------+------------------------------------------------------------------------+ 
| MID Telescope Component                  |            FQDN                                                        | 
+==========================================+========================================================================+ 
| TMC                                      |  ska_mid/tm_central/central_node                                       |
+------------------------------------------+------------------------------------------------------------------------+
| SDP-LMC                                  |  ska_mid/sdp_lmc/{id}                                                  |
+------------------------------------------+------------------------------------------------------------------------+
| CSP-LMC                                  |  ska_mid/csp_lmc/{id}                                                  |
+------------------------------------------+------------------------------------------------------------------------+
| MCCS-LMC                                 |  ska_mid/mccs_lmc/{id}                                                 |    
+------------------------------------------+------------------------------------------------------------------------+


**NOTE** : {id} is the identifier for the deployed subarray.
           For instance, if two subarrays are deployed:

            Subarray 1 will be:
           
                TMC Subarray : ska_mid/tm_central/central_node/01
           
                SDP-LMC : ska_mid/sdp_lmc/01
           
                CSP-LMC : ska_mid/csp_lmc/01
           
                MCCS-LMC : ska_mid/mccs_lmc/01
         
            For Subarray 2:

                TMC Subarray : ska_mid/tm_central/central_node/02
         
                SDP-LMC : ska_mid/sdp_lmc/02
         
                CSP-LMC : ska_mid/csp_lmc/02
         
                MCCS-LMC : ska_mid/mccs_lmc/02
