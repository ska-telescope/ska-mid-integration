All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[unreleased]
************
* Update ska-tmc-sdpleafnodes v0.21.1 to fix hardcoded sdp configure interface 0.3.
* Update ska-tmc-centralnode v0.18.1 (contains latest telmodel to fix SKB-672 for low side).

[1.0.0-rc.1]
************
* Resolved SKB-714, SKB-690
* Added `domain` field in values.yaml. The domain is `mid-tmc`
* Added `family` and `member` field in deviceServers of each controller leafnode device in values.yaml
* Added `family` field in deviceServers of each subarray leafnode devices in value.yaml
* Updated the TRLs of TMC low devices as per ADR-9
* ska_mid/tm_central/central_node - mid-tmc/central-node/0              
* ska_mid/tm_subarray_node/1 - mid-tmc/subarray/01            
* ska_mid/tm_leaf_node/csp_master - mid-tmc/leaf-node-csp/0
* ska_mid/tm_leaf_node/sdp_master - mid-tmc/leaf-node-sdp/0
* ska_mid/tm_leaf_node/csp_subarray01 - mid-tmc/subarray-leaf-node-csp/01
* ska_mid/tm_leaf_node/sdp_subarray01 - mid-tmc/subarray-leaf-node-sdp/01
* ska_mid/tm_leaf_node/d0001 - mid-tmc/leaf-node-dish/ska001
* Updated CentralNode version to 0.18.0
* Updated DishLeafNode version to 0.20.0
* Updated SdpLeafNode version to 0.21.0
* Updated CspLeafNode version to 0.24.0
* Updated SubarrayNode version to 0.30.1

[0.25.0-rc.4]
*************
* Updated event receiver from central node
* Tested  timeout and error propagation for Scan/EndScan/End
* Resolved SKB-709 caused due to dishleafnode unavailability

[0.25.0-rc.3]
*************
* Added Configure functionality for ADR-63 based json

[0.25.0-rc.2]
*************
* Fixed RTD

[0.25.0-rc.1]
*************
* Following bugs are fixed on the tmc-dish interface:
  * SKB-469
  * SKB-606
  * SKB-661
* Fixed SKB-658 on all the TMC devices.

[0.24.0]
********
* TMC Mid full release 0.24.0 as per REL-1555

[0.24.0-rc.3]
*************
* Utilised CDM v.12.6.0 on ska-tmc-subarraynode.

[0.24.0-rc.2]
*************
* Updated following TMC nodes:
  * SDP subarray leaf node to fix SKB-699.
  * Central Node to fix event receiver and telescope on command.
  * Subarry Node to fix abort aggregation and SKB-512.
  * Dish leaf node to fix abort lock and scheduler blocking issue.
  * Fixed bug SKB-516 and SKB-536.
  * CSP subarray leaf node to fix SKB-666
  * Fixed bug SKB-525.
  * Fixed bug SKB-665 on central node.
  
[0.24.0-rc.1]
*************
* Verified the TMC-CSP with ADR-99 interface updates

[0.23.0-rc.1]
*************
* Verified the TMC-Dish interface timeout and error propagation functionality

[0.22.8]
********
* Resolved SKB-467, SKB-495, SKB-511 and SKB-530
* Track command will not be invoked from Dish leaf node if pointingState of Dish is TRACK/SLEW

[0.22.6]
********
* Resolved SKB-509
* Updated TMC to support TMC-CSP Configure interface v.3.0

[0.22.8-rc.1]
*************
* Updated ska-tmc-centralnode v0.16.8 to resolve skb-495
* Updated ska-tmc-cspleafnode v0.21.2 to resolve skb-495 and skb-530

[0.22.7-rc.1]
*************
* Updated ska-tmc-dishleafnode v0.17.6 to resolve SKB-511 and SKB-467
* Track command will not be invoked from Dish leaf node if pointingState of Dish is TRACK/SLEW

[0.22.6-rc.1]
*************
* Updated ska-tmc-subarraynode v.0.23.4 to resolve SKB-509
* TMC supporting TMC-CSP Configure interface v.3.0

[0.22.5]
**********
* Updated dish leaf node version 0.17.3 to resolve SKB-502
* Updated central node to 0.16.4 to resolve SKB-434

[0.22.4]
************
Fixed *SKB-497*

[0.22.3]
************
*TMC Dish Pointing (ADR-95 and ADR-76)*
  * Utilise Dishleafnode v0.17.1 to use correction key from Config json.
  * Test cases are implemented for correction key [{UPDATE},{RESET},{MAINTAIN}].

[0.22.2]
************
*Read the Docs warnings addressed*


[0.22.1]
************
*Observation State Aggregation Logic improvements*
  * Rule engine is used to define rules for ObsState
  * EventDataStorage class introduced to store event related data

[0.22.0]
************
* Utilised base class v1.0.0 and pytango 9.5.0 on TMC nodes*
    * Utilised ska-tmc-common v0.17.6 for tango helper devices.
    * Implemented queue according to support base classes v1.0.0.
    * Refactored command allowed method to put commands in queue.
    * Implemented command allowed methods for observation-specific commands to allow/reject the queued task: `ResultCode.NOT_ALLOWED/ResultCode.REJECTED`.
    * Refactored error propagation implementation on SubarrayNode, CentralNode, and TMC leaf nodes to handle `longrunningcommandresult` attribute new format in case of raised exceptions.
    * Refactored error propagation implementation to handle `longrunningcommandresult` event for `ResultCode.NOT_ALLOWED`, `ResultCode.REJECTED`, and `ResultCode.FAILED`.
    * Refactored all the integration tests (pairwise and with mocks) for TMC Mid according to `longrunningcommandresult` attribute value.

* Utilised `cspsubarrayleafnode` v0.19.1 with fixed `SKB-413`: Mid Delay Model code pointing to wrong dishes.
    * Implemented antenna parameters objects to generate according to mid_json layout.
    * Corrected Mid Delay Model to point to SKA or MKT dish according to assigned receptors.

* Utilised `dishleafnode` v0.16.3 Patch release for `SKB-419` fix from branch `SAH-1566`.

[0.21.2]
************
* Fix image link reference for DishLeafNode.

[0.21.1]
************
* Resolve `SKB-419`.
* Resolve `SKB-384` -  Currently, across all devices in TMC, there are no polled attributes (after our work on `SKB-384`). TMC monitors the attributes of other devices using event subscription methods. Unlike polling, which involves continuous querying, event subscription relies on a push-based mechanism. When a device generates an event (such as an attribute value change), the Tango system notifies all subscribed clients. As a result, there is no ongoing polling loop; TMC only receives updates when events occur."
* Note: This release - `REL-1623` is from `SAH-1564`.

[0.21.0]
************
* Improvement as per ADR-76 changes are done in Dish Leaf node and Subarray Node.
* Enabled ProgramTrackTable.
* Fixed CORBA issues in dish leaf node while execution of commands.

[0.20.1]
************
* Integrate TMC-Dish Scan functionality implementation.
* This release is from branch `sah-1524`.

[0.20.0]
************
* `SP-4028` Delay Model Improvements.
* `SKB-329` and `SKB-330` bug fixes on `CspSubarrayLeafNode` v0.16.2.
* Updated affected BDD test case - `XTP-32140`.

[0.19.2]
***********
* Updated Subarray Node to v0.18.0 that resolves the `SKB-331` and gets rid of hardcoded interface values.
* Fix bug `SKB-337`.
* Updated the kValue range to 1 to 1177.
* kValue range is a device property.
* Configure command gets accepted if the kValue for assigned dishes is either all the same or all different.

[0.19.1]
************
* Intermediate chart with TMC updates to work with `dish-lmc` chart 3.0.0.
* Fixed issues in the tests.

[0.19.0]
************
* Aligned delay model json as per ADR-88.
* `DelayCadence`, `DelayValidity`, and `DelayAdvancedTime` values are configurable.
* Fixed `SKB-300`.

[0.18.0]
************
* Integrated `ska-tmc-dishleafnode` with program track table into `ska-tmc-mid-integration` (SP-3987).