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

  - **Subarray Health State** (only for dishes allocated to that subarray)
  - **Telescope Health State** (across all dishes contributing to the telescope)

Health state aggregation logic
------------------------------

The Dish Leaf Node derives its health state solely based on its own validation results:

* If **both kValue and GPM validations are OK**, the dish health is **HealthState.OK**.
* If **exactly one validation fails**, the dish health is **HealthState.DEGRADED**.
* If **multiple validations fail**, the dish health is **HealthState.FAILED**.

This logic applies uniformly to **any number of dishes**.

Subarray and telescope health states are derived by aggregating the health states of all contributing dishes.

.. note::

   **Subarray health aggregation**

   * Only dishes **currently allocated to a given subarray** contribute to that subarray’s health state.
   * Dishes that are not allocated are **excluded** from subarray health calculations.
   * The subarray health state is derived by aggregating the health states of all allocated dishes:

     * All dishes OK → **HealthState.OK**
     * At least one DEGRADED and none FAILED → **HealthState.DEGRADED**
     * All FAILED → **HealthState.FAILED**


Validation outcomes and resulting health states
-----------------------------------------------

The table below illustrates typical validation scenarios using symbolic dish sets (D1…Dn).

+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| No | Dish        | kValue Validation | GPM Validation    | Dish Leaf Node Health  | Subarray Health State | Telescope Health State |
+====+=============+===================+===================+========================+=======================+========================+
| 1  | All dishes  | ResultCode.OK     | ResultCode.OK     | HealthState.OK         | HealthState.OK        | HealthState.OK         |
|    | (D1…Dn)     | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 2  | D1 affected | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   | HealthState.DEGRADED  | HealthState.DEGRADED   |
|    | D2…Dn       | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 3  | D1 affected | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     | HealthState.DEGRADED  | HealthState.DEGRADED   |
|    | D2…Dn       | ResultCode.OK     | ResultCode.OK     | HealthState.OK         |                       |                        |
+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 4  | D1 affected | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     | HealthState.FAILED    | HealthState.FAILED     |
|    | D2…Dn       | ResultCode.FAILED | ResultCode.OK     | HealthState.FAILED     |                       |                        |
+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+
| 5  | All dishes  | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   | HealthState.FAILED    | HealthState.DEGRADED   |
|    | (D1…Dn)     | ResultCode.OK     | ResultCode.FAILED | HealthState.DEGRADED   |                       |                        |
+----+-------------+-------------------+-------------------+------------------------+-----------------------+------------------------+


Alarm behaviour
---------------

To ensure configuration mismatches are visible to operators, explicit alarm rules are configured at the Dish Leaf Node level :

The following conditions are evaluated and raised as alarms:

* kValue validation alarm
    An alarm is raised when the kValue reported by a dish does not match the last successfully applied kValue maintained by TMC
    (kValue validation result = ResultCode.FAILED)

* GPM validation alarm
    An alarm is raised when the GPM version reported by a dish does not match the last successfully applied GPM version maintained by TMC
    (GPM validation result = ResultCode.DEGRADED)

* Any validation mismatch detected by a Dish Leaf Node raises a corresponding alarm.