.. _`Applying Array Layout Through TMC`:

==========================================
 Apply Array Layout Through TMC
==========================================

Overview
--------
 
This document explains how TMC Mid manages and applies the Array Layout configuration.
This capability allows the  TMC to manage, validate,  
and distribute layout data across all subarrays and leaf nodes.

The Array Layout handling begins during the **AssignResources** process, where it  
includes a ``telmodel`` section specifying the source and path of the layout data.  
The SubarrayNode retrieves this reference, downloads and validates the layout,  
and later passes the processed data inline to the Dish and CSP leaf nodes during the **Configure** step.  


Central Node
------------

The **Central Node** manages the default and active Array Layout configurations used across the TMC.  
It defines and maintains the reference to the array layout data that will be applied by SubarrayNodes during resource assignment and configuration.

**Command:**  
``AssignResources(payload)``

Two attributes are introduced for this purpose:

- **DefaultArrayLayoutURL**

  Specifies the default array layout source and path to be used when the system starts, or when no specific layout is provided.  
  This ensures that the Central Node always has a valid reference to a baseline layout configuration.

- **ArrayLayoutURL**

  Indicates the current array layout configuration actively in use.  
  This attribute can be updated dynamically when new resources are assigned, allowing operational flexibility without requiring a restart or redeployment.

When the **AssignResources** command is executed, the Central Node checks whether the request includes a custom array layout reference. 
If a `telmodel` section is provided in the request, the Central Node updates its **ArrayLayoutURL** with the new layout information.  
If no `telmodel` data is specified, the **DefaultArrayLayoutURL** is used instead.

Using the AssignResources command on the Central Node, with the telmodel section included in the JSON payload (as shown in the example), the Array Layout can be applied to leaf nodes.

**Example AssignResources JSON**

The example below shows ``telmodel`` section in the AssignResources payload for the Central Node:

.. code-block:: json

    {
      "interface": "https://schema.skao.int/ska-mid-tmc-assignresources/4.3",
      "transaction_id": "txn-00000-assign-mid-4.3",
      "subarray_id": 1,
      "telmodel": {
        "source_uris": [
          "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"
        ],
        "array_layout_path": "instrument/ska1_mid/layout/mid-layout.json"
      },
      "dish": {
        "interface": "https://schema.skao.int/ska-tmc-dish-assignresources/1.0",
        "receptor_ids": ["SKA001","SKA036","SKA100"]
      },
      "sdp": {
        "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
        "execution_block": {
          "eb_id": "eb-mid-test-00001",
          "context": {},
          "beams": [
            { "beam_id": "vis0", "function": "visibilities" }
          ],
          "scan_types": [
            {
              "scan_type_id": ".default",
              "beams": {
                "vis0": {
                  "channels_id": "vis_channels",
                  "polarisations_id": "all"
                }
              }
            }
          ]
        },
        "resources": {
          "receptors": ["SKA001", "SKA002"],
          "receive_nodes": 1
        }
      },
      "csp": {
        "interface": "https://schema.skao.int/ska-csp-assignres/1.0",
        "subarray_id": 1
      }
    }


Subarray Node
-------------

The **SubarrayNode** manages the download, validation, and distribution of the Array Layout data.

When the **AssignResources** command is received, the SubarrayNode extracts the **Array Layout URI** provided.  
It then downloads the layout data from the specified TelModel source and stores the URI in a memorized attribute (**arrayLayoutUri**) to ensure persistence across restarts.

Once the layout is successfully downloaded and validated, it becomes available for later configuration steps.  
During the **Configure** phase, the SubarrayNode retrieves the validated Array Layout data and sends it inline to its connected leaf nodes, ensuring each element of the subarray (Dish and CSP Subarray) receives the correct layout information.

Dish Leaf Node
--------------

Each **DishLeafNode** receives the validated Array Layout data inline as part of the **Configure** from its SubarrayNode.  

Once received, the Dish Leaf Node parses the layout information and applies it.  
This layout information enables the Dish to compute and generate the **PTT**.

If any issues occur while processing the layout data, the Dish Leaf Node retains the last valid configuration and reports an error back to the TMC.

CSP Subarray Leaf Node
----------------------

The **CSP Subarray Leaf Node** also receives the validated Array Layout data inline within the **Configure**  sent from the SubarrayNode.  

Upon receiving the configuration, the CSP Subarray Leaf Node parses the layout data and uses it to perform **delay calculations**.  

If the CSP Leaf Node encounters any issues while applying the layout, it maintains the last successfully applied configuration and reports an error to the TMC.  


Persistence and Restart Behavior
--------------------------------

Both **Central Node** and **Subarray Node** persist their `ArrayLayoutdata` attributes.

- On restart, these values are automatically reloaded.
- No new **AssignResources** call is needed after restart.
- **ReleaseResources** does not clear these values; they remain until overwritten.

References
----------

For detailed design and implementation notes, refer to:  
`Spike HM-749: Implementation Details for Array Layout <https://confluence.skatelescope.org/display/SWSI/Spike+-+HM-749+%3A++Implementation+Details+for+Array+Layout>`_