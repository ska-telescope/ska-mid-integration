.. _`Applying GPM Through TMC`:

==========================================
Steps to Apply GPM on Dish(es) Through TMC
==========================================

Overview
--------

TMC Mid supports Global Pointing Model (GPM) configuration starting from version 1.9.0.

This document describes ways to apply the GPM using TMC.


Central Node
------------

The **SetGlobalPointingModel** command is available on the TMC and is used to apply the Global Pointing Model (GPM) to specified dishes.

Before initializing the TMC, ensure the following parameters are correctly configured in the values.yaml file:

**interface**: Specifies the URL for the GPM schema interface.

**data_sources_prefix**: Base URI for GPM data repositories (e.g., CAR URLs)

**file_path_prefix**: The relative path to GPM data within the repository.

These parameters are mandatory and are used by the TMC to construct the correct path for retrieving the GPM JSON file based on the specified version and band.

For detailed syntax, input examples, and workflow diagrams, please refer to |TMC GPM Workflow|_.

.. |TMC GPM Workflow| replace:: **TMC GPM Workflow**
.. _TMC GPM Workflow: https://confluence.skatelescope.org/x/V4TtEQ

Dish Leaf Node
--------------

Using the **ApplyPointingModel** command on the Dish leaf node, the Global Pointing Model (GPM) can be applied to the corresponding connected dish.

Example:

.. code-block:: python

    gpm_input = json.dumps({
    "interface": "https://schema.skao.int/ska-mid-dish-gpm/1.2",
    "tm_data_sources": ["car://gitlab.com/ska-telescope/ska-tmc/ska-tmc-simulators?main#tmdata"],
    "tm_data_filepath": "instrument/ska_mid1/global_pointing_model_data/gpm-ska001-Band_1.json"
    })

    dln_proxy = tango.DeviceProxy("mid-tmc/leaf-node-dish/ska001")

    dln_proxy.ApplyPointingModel(gpm_input)

**tm_data_sources**: Specifies the base location(s) (e.g., CAR URIs) where the Telescope Model (TM) data is stored.

**tm_data_filepath**: Provides the relative path within the data source to locate the specific GPM JSON file.




