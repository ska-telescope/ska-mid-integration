
.. _`Five Point Calibration Scan`:

TMC Five-Point Calibration Scan
===================================

This guide provides instructions for performing a **five-point calibration scan** with TMC.

The procedure is intended for operators, to establish pointing calibration solutions that will later be applied during science observations.

Overview
--------

- The subarray must first be in the ``READY`` observation state.
- The calibration scan sequence includes:

  * One central pointing scan (reference),

  * Four offset scans (north, south, east, west) using partial configuration JSONs.

- After calibration, the subarray returns to ``READY`` and the calibration solutions are available for subsequent science scans.

Preconditions
-------------

* TMC Subarray Node and its connected subsystems (SDP, CSP, Dish Leaf Nodes) are online and reachable.
* Required JSON configuration files are available:

  - ``scan_mid.json`` (central reference scan)

  - ``partial_configuration_1.json`` to ``partial_configuration_4.json`` (offset scans)

  - ``configure_mid.json`` (post-calibration science configuration)

  - ``receive_address_mid.json`` (SDP calibration solution addresses)

* Resources have already been assigned to the subarray and it is in the ``READY`` observation state.
* Commands can be sent to the Subarray Node using the standard operational interface.

Step-by-Step Procedure
----------------------

1. **Confirm Subarray state**

   - Verify that the Subarray Node is in ``READY``.

   - If not, assign resources and configure until ``READY``.

2. **Central pointing scan**

   - Send a ``Scan`` command with ``scan_mid.json``.

   - Observe state transitions: ``READY → SCANNING → READY``.

3. **Offset scans**

   - Perform four offset scans using partial configuration JSONs:
     
     +--------------------------------------+---------------------------------------------+
     | JSON file                            | Offset details                              |
     +======================================+=============================================+
     | ``partial_configuration_1.json``     | CA offset = 0.0, IE offset = +5.0 arcsec    |
     +--------------------------------------+---------------------------------------------+
     | ``partial_configuration_2.json``     | CA offset = 0.0, IE offset = −5.0 arcsec    |
     +--------------------------------------+---------------------------------------------+
     | ``partial_configuration_3.json``     | CA offset = +5.0 arcsec, IE offset = 0.0    |
     +--------------------------------------+---------------------------------------------+
     | ``partial_configuration_4.json``     | CA offset = −5.0 arcsec, IE offset = 0.0    |
     +--------------------------------------+---------------------------------------------+

   - For each offset:

     * Send ``Configure`` with the partial configuration JSON.

     * Send ``Scan``.

     * Confirm Subarray transitions to ``SCANNING`` and returns to ``READY``.

4. **Validate pointing**

   - After each scan, check that each dish reports updated ``actualPointing`` values.

   - Ensure no errors were reported in command results.

5. **Apply calibration and proceed to science scan**

   - Send a ``Configure`` command with ``configure_mid.json``.

   - TMC will fetch calibration solutions from SDP according to ``receive_address_mid.json``.

   - Confirm calibration solutions are applied to dishes.

   - Subarray should return to ``READY``.

   

Failure to Complete Five-Point Scan
-----------------------------------

If the calibration sequence does not complete:

* **Check observation state transitions**

  - Verify Subarray moves to ``SCANNING`` during each scan and returns to ``READY``.

* **Inspect Dish Leaf Nodes**

  - Ensure ``actualPointing`` is updated after each offset scan.

* **Verify JSON payloads**

  - Confirm offsets are correct and ``"partial_configuration": true`` is included.

* **Check calibration availability**

  - Ensure SDP has published calibration data at the addresses listed in ``receive_address_mid.json``.

* **Re-run failed steps if required**

  - If an offset scan fails, repeat that partial configuration and scan.

* **Proceed to science only after success**

  - Do not configure for science scans until all five calibration scans are complete.

JSON Interface References
-------------------------

* TMC Configure schema: https://schema.skao.int/ska-tmc-configure/2.2

* Example partial configurations:

  **partial_configuration_1.json**

  .. code-block:: json

     {
         "interface": "https://schema.skao.int/ska-tmc-configure/2.2",
         "transaction_id": "txn-....-00002",
         "pointing": {
             "target": {
                 "ca_offset_arcsec": 0.0,
                 "ie_offset_arcsec": 5.0
             }
         },
         "tmc": {
             "partial_configuration": true
         }
     }

  **partial_configuration_2.json**

  .. code-block:: json

     {
         "interface": "https://schema.skao.int/ska-tmc-configure/2.2",
         "transaction_id": "txn-....-00003",
         "pointing": {
             "target": {
                 "ca_offset_arcsec": 0.0,
                 "ie_offset_arcsec": -5.0
             }
         },
         "tmc": {
             "partial_configuration": true
         }
     }

  **partial_configuration_3.json**

  .. code-block:: json

     {
         "interface": "https://schema.skao.int/ska-tmc-configure/2.2",
         "transaction_id": "txn-....-00004",
         "pointing": {
             "target": {
                 "ca_offset_arcsec": 5.0,
                 "ie_offset_arcsec": 0.0
             }
         },
         "tmc": {
             "partial_configuration": true
         }
     }

  **partial_configuration_4.json**

  .. code-block:: json

     {
         "interface": "https://schema.skao.int/ska-tmc-configure/2.2",
         "transaction_id": "txn-....-00005",
         "pointing": {
             "target": {
                 "ca_offset_arcsec": -5.0,
                 "ie_offset_arcsec": 0.0
             }
         },
         "tmc": {
             "partial_configuration": true
         }
     }

* Receive address schema (``receive_addresses_mid.json``):

  .. code-block:: json

     {
         "science_A": {
             "vis0": {
                 "function": "visibilities",
                 "host": [
                     [0, "192.168.0.1"],
                     [400, "192.168.0.2"],
                     [744, "192.168.0.3"],
                     [1144, "192.168.0.4"]
                 ],
                 "port": [
                     [0, 9000, 1],
                     [400, 9000, 1],
                     [744, 9000, 1],
                     [1144, 9000, 1]
                 ],
                 "mac": [
                     [0, "06-00-00-00-00-00"],
                     [744, "06-00-00-00-00-01"]
                 ],
                 "delay_cal": "mid-sdp/telstate/rcal0/delay",
                 "pointing_cal": "tango://mid-sdp/queueconnector/01/pointing_cal_{dish_id}"
             }
         }
     }






