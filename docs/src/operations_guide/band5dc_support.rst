=======================================
Band 5 Downconversion (Band5DC) Support
=======================================

Overview
--------

This document describes the support added for **Band 5 downconversion (Band5DC)** 
within the ``ska-tmc-mid-integration`` repository.  
These updates ensure correct propagation of Band 5 specific configuration 
parameters across Dish, SubarrayNode, and CSP components.

Changes Introduced
------------------

1. **New JSON files added** for Band5DC support:

   - ``AssignResources_band5_dc.json``  
   - ``Configure_band5_dc.json``

2. **SubarrayNode Enhancements**:
   
   - Logic added to propagate ``band5_downconversion_subband`` from 
     ``dish`` block into the ``csp.common`` block during configuration.

3. **Integration Updates**:

   - Validation of new CDM schema fields with Band 5 downconversion.  
   - Alignment with the latest ska-tmc-cdm releases.

How to Use
----------

1. Use the **AssignResources_band5_dc.json** file when assigning resources 
   to a Subarray that requires Band 5 downconversion.  

2. Use the **Configure_band5_dc.json** file to configure the Subarray 
   with Band 5 specific parameters such as the ``band5_downconversion_subband``.  

3. Ensure that the SubarrayNode propagates the Band 5 parameters to CSP.  
   This allows CSP to correctly configure Band 5 receivers with the expected 
   subband values.

Outcome
-------

- Band 5 downconversion support is now fully integrated into the Mid 
  integration environment.  
- Provides confidence that Band 5 specific parameters are handled correctly 
  across Dish, SubarrayNode, and CSP.  

References
----------

For more details, see the ADR on Band 5 Downconverter design and interface definitions:  
`ADR-102: Band 5 observations in AA 0.5 - detailed design and interface definitions for execution of scans using Band 5 Downconverter <https://confluence.skatelescope.org/display/SWSI/ADR-102+Band+5+observations+in+AA+0.5+-+detailed+design+and+interface+definitions+for+execution+of+scans+using+Band+5+Downconverter>`_
