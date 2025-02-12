TMC Mid Deployment
=======================

TMC Mid deployment comes with following components:

1. **Central Node** 

2. **Subarray Node**

3. **Csp Master Leaf Node**

4. **Csp Subarray Leaf Node**

5. **Sdp Master Leaf Node**

6. **Sdp Subarray Leaf Node**

7. **Dish Leaf Node**

Configurable options
--------------------

* a. **instances** : User can provide the array of device server deployment instances required for node.

    Default for nodes are:

    #. **Central Node** : ["01"] 

    #. **Csp Master Leaf Node** : ["01"] 

    #. **Sdp Master Leaf Node** : ["01"]

* b. **subarray_count** : User can set this subarray count according to number of device server deployment instances required for node. 

    Default value for nodes is 2.

    #. **Subarray Node**

    #. **Csp Subarray Leaf Node**

    #. **Sdp Subarray Leaf Node** 

* c. **dish_name** : User can set this by providing the list of TRLS using global.namespace_dish.dish_names

    Default Value for dish leaf node is

    #. **Dish Leaf Node** : ["001", "036", "063", "100"]

* d. **file** : User can provide custom device server configuration file to  nodes.Default is  `configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-integration/-/blob/main/charts/ska-tmc-mid/data/>`_

* e. **enabled** : User can opt to disable any node by setting this value to False.Default is True for all nodes.

* f. Variables under **global** section

    #. **tmc_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SubarrayNode.

    #. **csp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspSubarrayLeafNode.

    #. **sdp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpSubarrayLeafNode.

    #. **csp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspMasterLeafNode.

    #. **sdp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpMasterLeafNode.

    #. **csp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of CSP Subarray.

    #. **sdp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SDP Subarray.

    #. **csp_master** : This value is present under global, User can use this to change the FQDN of CSP Master.

    #. **sdp_master** : This value is present under global, User can use this to change the FQDN of SDP Master.

    #. **dish_suffix** : This value is present under global, User can use this to change the FQDN suffix of Dish Master.

    #. **dish_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of DishLeafNode.

* g. Variables under **deviceServers.centralnode** section

    #. **DishIDs** : User can set this value to provide the ID's of dishes present in the deployment. Default is ["SKA001", "SKA036", "SKA063", "SKA100"]

    #. Variables under **DishVccConfig** section

        #. **DishVccUri** :  This refers to the URI for Dish VCC Configuration. Currently defaults to "car://gitlab.com/ska-telescope/ska-telmodel-data?ska-sdp-tmlite-repository-1.0.0#tmdata".

        #. **DishVccFilePath** :  This refers to the file path for Dish VCC Configuration. Currently defaults to "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json".
        
        #. **DishKvalueAggregationAllowedPercent** :  This refers to the percentage of the dishes to be considered for DishKValue aggregation. Currently all the dishes are considered therefore defaults to "100.0".

    #. Variables under **KValueValidRange** section

       #. **min** :  This refers to the lower limit of the valid k-value range. Currently defaults to 1.

       #. **max** :  This refers to the upper limit of the valid k-value range. Currently defaults 1177.
    
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 2 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 2 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 120 seconds.

    #. **DishVccInitTimeout** :  This refers to the timeout (in seconds) for the dish vcc initialization. Currently defaults to 180 seconds.

* h. Variables under **deviceServers.subarraynode** section
    
    #. **DishIDs** : User can set this value to provide the ID's of dishes present in the deployment. Default is ["SKA001", "SKA036", "SKA063", "SKA100"]

    #. **CspAssignResourcesInterfaceURL** : Interface version for CSP assign resources command. Currently defaults to "https://schema.skao.int/ska-csp-assignresources/2.0".
    
    #. **CspScanInterfaceURL** : Interface version for CSP scan command. Currently defaults to "https://schema.skao.int/ska-csp-scan/2.0".
    
    #. **SdpScanInterfaceURL** : Interface version for SDP scan command. Currently defaults to "https://schema.skao.int/ska-sdp-scan/0.4".

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 110 seconds.
    
    #. **AbortCommandTimeOut** :  This refers to the timeout for the Subarray ABORTED obsState transition. Once the AbortCommandTimeOut exceeds, SubarrayNode transitions to obsState FAULT. Currently defaults to 130 seconds.

* i. Variables under **deviceServers.sdpsubarrayleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* j. Variables under  **deviceServers.sdpmasterleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* k. Variables under **deviceServers.cspmasterleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* l. Variables under **deviceServers.cspsubarrayleafnode** section

    #. **DelayCadence** :  This refers to the time difference (in seconds) between each publication of delay values to the `delayModel` attribute on the `CspSubarrayLeafNode`. Currently defaults to 10 seconds.

    #. **DelayValidityPeriod** : This represents the duration (in seconds) for which delay values remain valid after being published. Currently defaults to 20 seconds.

    #. **DelayModelTimeInAdvance** : This indicates the time in seconds by which delay values need to be available in advance. Currently defaults to 30 seconds.
    
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

    #. **TelmodelSource** :  This refers to the telmodel source for array layout. Currently defaults to "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata".

    #. **TelmodelPath** :  This refers to the telmodel path for array layout. Currently defaults to "instrument/ska1_mid/layout/mid-layout.json".

* m. Variables under **deviceServers.dishleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 1.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 1.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 90 seconds.

    #. **MaxTrackTableRetry** :  This refers to the maximum retries for the programTrackTable write operation. Currently defaults to 3.

    #. **TrackTableRetryDuration** :  This refers to the retry duration (in seconds) for programTrackTable write operation in seconds. Currently defaults to 0.2 seconds.

    #. **DishAvailabilityCheckTimeout** :  This refers to the timeout for the dish availability check during intialisation. This property is for internal use. Currently defaults to 3 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* n. Variables under **deviceServers.dishpointingdevice** section

    #. **TrackTableUpdateRate** : This refers to the rate (in seconds) at which a tracktable is supplied to the DishManager. Currently defaults to 50 seconds.

    #. **TrackTableInAdvance** : This refers to the time in advance at which programTrackTable needs to be provided. Currently defaults to 7 seconds.

    #. **ElevationMaxLimit** : This refers to the maximum elevation allowed for observation. Currently defaults to 90.0.

    #. **ElevationMinLimit** : This refers to the minimum elevation allowed for observation. Currently defaults to 15.0.

    #. **AzimuthMaxLimit** : This refers to the Maximum value of Azimuth where dish can point. Currently defaults to 270.0.

    #. **AzimuthMinLimit** : This refers to the Minimum value of Azimuth where dish can point. Currently defaults to -270.0.