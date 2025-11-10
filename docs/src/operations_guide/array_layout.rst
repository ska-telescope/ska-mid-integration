.. _`Applying Array Layout Through TMC`:

==========================================
Applying Array Layout Through TMC
==========================================

Overview
--------

This page provides instructions for applying an **Array Layout** configuration through the TMC for **SKA-Mid**.
 
TMC allows operators to specify which Array Layout should be used for observations by providing its reference in the **AssignResources** command.

When the Array Layout is applied successfully, TMC distributes it automatically to all relevant subsystems during configuration.  
No manual updates are required on Dish or CSP components.

How to Apply Array Layout
-------------------------

The Array Layout is specified during the **AssignResources** step using the ``telmodel`` section in the JSON payload.

1. **Prepare the AssignResources JSON**

   Add the ``telmodel`` block to your AssignResources payload.  
   It defines the source and path of the Array Layout data in the TelModel repository.

   **Example:**

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
          "receptor_ids": ["SKA001", "SKA036", "SKA100"]
        },
        "csp": {
          "subarray_id": 1
        },
        "sdp": {
          "resources": {
            "receptors": ["SKA001", "SKA002"]
          }
        }
      }

   .. note::

      Only the ``telmodel`` section is new in this payload.
      Other fields follow the standard AssignResources format.

2. **Send the AssignResources command**

   - Send the above JSON to the **Central Node** using the standard AssignResources interface.  
   - TMC automatically retrieves and validates the specified Array Layout.

   If the ``telmodel`` section is not provided, the **default Array Layout** configured in the Central Node will be used.

3. **Verify the layout reference**

   - After AssignResources completes successfully, Check that the **ArrayLayoutURL** attribute on the Central Node shows the expected layout reference.
   - The Subarray can now be configured for observations using this layout.

Central Node Attributes
-----------------------

The Central Node maintains two key attributes for Array Layout management:

- **DefaultArrayLayoutURL**  
  The baseline layout used when no custom layout is specified in the AssignResources payload.
  This default layout remains active system-wide until a new layout is explicitly provided, at which point the ArrayLayoutURL attribute is updated to reflect the overridden configuration.

- **ArrayLayoutURL**  
  The currently active layout that was last applied.  
  This value updates automatically when a new layout is assigned.

Outcome
-------

Once applied, the selected Array Layout is used across all TMC-managed components:

- **Dish:**  
  The Dish nodes parses the layout data and uses it to generate the Program Track Table.

- **CSP:**  
  CSP Subarray Leaf Node parses the layout data and uses it to perform delay calculations.
