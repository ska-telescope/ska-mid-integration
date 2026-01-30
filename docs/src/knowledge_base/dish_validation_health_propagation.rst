Dish kValue and GPM Validation and Health Propagation
=====================================================

Overview
--------

Each dish reports configuration-related parameters (such as **kValue** and **GPM version**) to TMC. TMC also maintains the *last successfully applied* configuration.

To ensure the system is operating with consistent and expected configuration:

- TMC detects mismatches between the **kValue** and **GPM version** reported by each dish and what TMC considers as last applied.
- Based on the validation outcome, TMC derives and aggregates health states at multiple levels.
- Mismatched conditions are treated as alarms so that operators are promptly informed.

What is being validated
-----------------------

For each dish, two independent validations are performed:

- **kValue validation**  checks whether the kValue reported by the dish matches the value last applied by TMC.
- **GPM validation**  checks whether the GPM version reported by the dish matches the version last applied by TMC.

A validation result can be:

- ``ResultCode.OK``  the reported value matches TMC expected value.
- ``ResultCode.FAILED``  a mismatch is detected.

Where validations are performed
-------------------------------

- Validations are performed by the **Dish Leaf Node**.
- The Dish Leaf Node updates its own health state based on the validation results.
- These health states are then propagated and aggregated to higher levels:

  - **Subarray Health State**
  - **Telescope Health State**

Health state aggregation logic
------------------------------

The health state reflects the severity of the detected mismatches:

- If both kValue and GPM validations pass, the dish is considered **OK**.
- A single validation failure typically results in a **DEGRADED** health state.
- Multiple failures, or failures across multiple dishes, can escalate the health state to **FAILED**.

Subarray and telescope health states are derived by aggregating the health states of all contributing dishes.

Validation outcomes and resulting health states
-----------------------------------------------

The table below illustrates typical validation scenarios and how they affect health at different levels.

+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| No | Dish     | kValue Validation | GPM Validation    | Dish Leaf Node Health  | Subarray Health State | Telescope Health State |
+====+==========+===================+===================+========================+=======================+========================+
| 1  | SKA-001  | ResultCode.OK     | ResultCode.OK     | HealthState.OK         | HealthState.OK        | HealthState.OK         |
|    | SKA-036  | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 2  | SKA-001  | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   | HealthState.DEGRADED  | HealthState.DEGRADED   |
|    | SKA-036  | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 3  | SKA-001  | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     | HealthState.DEGRADED  | HealthState.DEGRADED   |
|    | SKA-036  | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 4  | SKA-001  | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     | HealthState.FAILED    | HealthState.FAILED     |
|    | SKA-036  | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     |                       |                        |
+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 5  | SKA-001  | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   | HealthState.FAILED    | HealthState.DEGRADED   |
|    | SKA-036  | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   |                       |                        |
+----+----------+-------------------+-------------------+------------------------+-----------------------+------------------------+

Alarm behaviour
---------------

To ensure mismatches are visible to operators:

- Alarm rules are configured for kValue and GPM validation failures.
- Any mismatch detected by the Dish Leaf Node is raised as an alarm in the system.