mid Telescope Deployment
========================

Components
----------

mid Telescope deployment includes the folmiding components:

1. **TMC**  
2. **SDP-LMC**  
3. **CSP-LMC**  
4. **DISH-LMC**  

Configurable Options
--------------------

Instances and Subarray Count
============================

1.Instances
-----------

Users can provide an array of device server deployment instances required for a component.

+---------------+---------------------------+
| **Component** | **Default**               |
+===============+===========================+
| TMC           | ["01"]                    |
+---------------+---------------------------+
| SDP-LMC       | ["01"]                    |
+---------------+---------------------------+
| CSP-LMC       | ["01"]                    |
+---------------+---------------------------+
| DISH-LMC      | ["001","100","036","100"] |
+---------------+---------------------------+

2.Subarray Count
----------------

Users can set the subarray count based on the number of required device server deployment instances.

+----------------------+----------------------------+
| **Component**        | **Default Subarray Count** |
+======================+============================+
| TMC                  | 2                          |
+----------------------+----------------------------+
| SDP-LMC              | 2                          |
+----------------------+----------------------------+
| CSP-LMC              | 2                          |
+----------------------+----------------------------+
| DISH-LMC             | 4                          |
+----------------------+----------------------------+



3. **Configuration File:**  
   Users can provide a custom device server configuration file.  
   `Configuration files <https://gitlab.com/ska-telescope/ska-mid-integration/-/tree/main/charts/ska-mid-integration/tmc_pairwise/>`_  

4. **Enabled:**  
   Almids users to enable or disable simulated components.  
   Default is `True` for all components.  
   `Makefile <https://gitlab.com/ska-telescope/ska-mid-integration/-/blob/main/Makefile/>`_

5. **Global FQDN Prefixes:**  

+----------------------------------------+----------------------------------------------------------------+
| **Setting**                            | **Description**                                                |
+========================================+================================================================+
| **tmc_subarray_prefix**                | FQDN prefix of TMC Subarray                                    |
+----------------------------------------+----------------------------------------------------------------+
| **csp_subarray_ln_prefix**             | FQDN prefix of CSP-LMC Subarray Leaf Node                      |
+----------------------------------------+----------------------------------------------------------------+
| **sdp_subarray_ln_prefix**             | FQDN prefix of SDP-LMC Subarray Leaf Node                      |
+----------------------------------------+----------------------------------------------------------------+
| **csp_master_ln_prefix**               | FQDN prefix of CSP-LMC Master Leaf Node                        |
+----------------------------------------+----------------------------------------------------------------+
| **sdp_master_ln_prefix**               | FQDN prefix of SDP-LMC Master Leaf Node                        |
+----------------------------------------+----------------------------------------------------------------+
| **csp_subarray_prefix**                | FQDN prefix of CSP Subarray                                    |
+----------------------------------------+----------------------------------------------------------------+
| **sdp_subarray_prefix**                | FQDN prefix of SDP Subarray                                    |
+----------------------------------------+----------------------------------------------------------------+
| **csp_master**                         | FQDN of CSP-LMC Master                                         |
+----------------------------------------+----------------------------------------------------------------+
| **sdp_master**                         | FQDN of SDP-LMC Master                                         |
+----------------------------------------+----------------------------------------------------------------+


Examples:
---------
+-------------+----------------------------------------------------------------------+
| **Setting** | **Description**                                                      |
+=============+======================================================================+
| **DishIDs** | User can set this value to provide the ID's of dishes present in the |
|             | deployment. Default is ["SKA001", "SKA036", "SKA063", "SKA100"].     |
+-------------+----------------------------------------------------------------------+




Additional few Central node specific configurations are:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------------+----------------------------------------------------------------------------+
| **Setting**            | **Description**                                                            |
+========================+============================================================================+
| **DishLeafNodePrefix** | User can set this value according to the FQDN prefix required by the       |
|                        | deployed dish leaf node devices. Default is "ska_mid/tm_leaf_node/d0".     |
+------------------------+----------------------------------------------------------------------------+
| **DishIDs**            | User can set this value to provide the ID's of dishes present in the       |
|                        | deployment. Default is ["SKA001", "SKA036", "SKA063", "SKA100"].           |
+------------------------+----------------------------------------------------------------------------+

**LeafNode Configuration**
^^^^^^^^^^^^^^^^^^^^^^^^^^
+------------------------+----------------------------------------------------------------------------+
| **Setting**            | **Description**                                                            |
+========================+============================================================================+
| **DishLeafNodePrefix** | User can set this value according to the FQDN prefix required by the       |
|                        | deployed dish leaf node devices. Default is "ska_mid/tm_leaf_node/d0".     |
+------------------------+----------------------------------------------------------------------------+
