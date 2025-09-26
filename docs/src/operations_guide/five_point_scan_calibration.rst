
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

* TMC Subarray Node must be online, reachable, and in the ``READY`` state.
* Required configuration JSONs (full or partial) are available:

  - `scan_mid.json <https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/tmc/ska-tmc-scan.html>`_ (central reference scan)

  - partial_configuration_1.json to partial_configuration_4.json (offset scans)

  - `configure_mid.json <https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/tmc/ska-tmc-configure.html>`_ (post-calibration science configuration)

  - `receive_address_mid.json <https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/sdp/ska-sdp-recvaddrs.html>`_ (SDP calibration solution addresses)

* Resources have already been assigned to the subarray and it is in the ``READY`` observation state.
* Commands can be sent to the Subarray Node using the standard operational interface.


Step-by-Step Procedure
----------------------

1. **Confirm Subarray state**

   - Verify that the TMC Subarray Node is online, reachable, and in the ``READY`` state.
   - If not, assign resources and configure until ``READY``.

2. **Perform five calibration scans**

   The calibration requires **five consecutive configuration + scan cycles**:

   * One central (reference) scan using a full configuration.
   * Four offset scans, each using a partial configuration that only changes the pointing offsets.
     All other subarray configuration parameters remain unchanged.

   For each cycle:

   - Send the appropriate ``Configure`` command (full or partial).
   - Send a ``Scan`` command.
   - Observe the state transitions: ``READY → SCANNING → READY``.

   .. note::

      The procedure is the same regardless of whether the configuration is
      full (central scan) or partial (offset scans). The difference lies only in
      the pointing offsets provided.

   **Example offsets for partial configurations**

   +--------------------------------------+---------------------------------------------+
   | JSON file (example)                  | Offset details                              |
   +======================================+=============================================+
   | ``partial_configuration_1.json``     | CA offset = 0.0, IE offset = +5.0 arcsec    |
   +--------------------------------------+---------------------------------------------+
   | ``partial_configuration_2.json``     | CA offset = 0.0, IE offset = −5.0 arcsec    |
   +--------------------------------------+---------------------------------------------+
   | ``partial_configuration_3.json``     | CA offset = +5.0 arcsec, IE offset = 0.0    |
   +--------------------------------------+---------------------------------------------+
   | ``partial_configuration_4.json``     | CA offset = −5.0 arcsec, IE offset = 0.0    |
   +--------------------------------------+---------------------------------------------+

3. **Validate pointing**

   After each scan, verify that the dishes have updated their ``actualPointing`` values
   and that no errors were reported in the command results.

4. **Apply calibration for science scans**

   Once all five calibration scans are complete:

   - Send a ``Configure`` command with the science configuration (for example, ``configure_mid.json``).
   - TMC will automatically fetch the calibration solutions from SDP using the addresses defined in ``receive_address_mid.json``.
   - Confirm that calibration solutions are applied to the dishes.
   - The Subarray should return to ``READY``.

   .. note::

      Applying calibration via ``Configure`` is a standard step before starting
      science observations. It is mentioned here only to highlight that the
      solutions obtained from the five-point scan will be applied at this stage.

5. **Proceed to science observations**

   - After confirming the calibration has been applied, the subarray is ready
     for science scans using the configured pointing solutions.

   

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

* `TMC Configure schema <https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/tmc/ska-tmc-configure.html>`_ 

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
                 "pointing_cal": "tango://mid-sdp/queueconnector/01/pointing_cal_{SKA001}"
             }
         }
     }






