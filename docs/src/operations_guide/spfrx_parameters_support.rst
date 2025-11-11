.. _`SPFRx Processing Parameters in TMC Configure`:

============================================================
SPFRx Processing Parameters in TMC Configure (v5.0+)
============================================================

Overview
--------

From schema version ``https://schema.skao.int/ska-mid-tmc-configure/5.0``, the ``dish`` section supports per-dish **SPFRx processing parameters** via ``spfrx_processing_parameters`` array.


Key Fields
----------

- ``dishes``: ``["all"]`` or list of dish IDs (e.g., ``["SKA001"]``)
- ``sync_pps``: ``true`` (required)
- ``attenuation_pol_x/y``: total attenuation (optional)
- ``attenuation_1/2_pol_x/y``: per-attenuator (all 4 required if used)
- ``saturation_threshold``: % SNR (0.0-1.0)
- ``noise_diode``: either ``psuedo_random`` **or** ``periodic`` (not both)

.. note::
   - Unlisted dishes use device defaults.
   - ``"all"`` allowed only in one block.
   - Dish cannot appear in multiple blocks.

Examples
--------

**All Dishes**

.. code-block:: json

   "spfrx_processing_parameters": [
     {
       "dishes": ["all"],
       "sync_pps": true,
       "attenuation_pol_x": 10,
       "attenuation_pol_y": 10,
       "saturation_threshold": 0.6
     }
   ]

**Per-Dish**

.. code-block:: json

   "spfrx_processing_parameters": [
     {
       "dishes": ["SKA001"],
       "sync_pps": true,
       "attenuation_1_pol_x": 20,
       "attenuation_2_pol_y": 10
     },
     {
       "dishes": ["SKA036"],
       "sync_pps": true,
       "saturation_threshold": 0.7
     }
   ]

Behavior
--------

- Omitted fields → revert to **device property defaults**
- ``noise_diode`` omitted → turned **OFF**
- ``sub_band``: optional (used only for band 5b)

TMC Mapping (v5.0+)
-------------------

- ``"all"`` → same config for all
- Explicit dishes → get their block
- Others → default: ``{ "dishes": ["SKAxxx"], "sync_pps": true }``