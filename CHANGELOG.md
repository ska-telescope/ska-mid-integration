All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.20.0]
* Integrate TMC-Dish Scan functionality implementation
[0.19.2]
***********
* Updated Subarray Node to v0.18.0 that resolves the SKB-331 and gets rid of hardcoded interface values
* Fix bug SKB-337
* Updated the kValue range to 1 to 1177.
* kValue range is a device property
* Configure command gets accepted if the kvalue for assinged dishes are either all same or all different

[0.19.1]
************
* Intermediate chart with TMC updates to work with dish-lmc chart 3.0.0
* Fixed issues in the tests

[0.19.0]
************
* Aligned delay model json as per ADR-88
* DelayCadence, DelayValidity and DelayAdvancedTime values are configurable
* Fixed SKB-300

[0.18.0]
************
* Integrated ska-tmc-dishleafnode with program track table into ska-tmc-mid-integration(SP-3987)