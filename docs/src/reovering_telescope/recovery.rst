.. _`Recovering Telescope Mid`:

How to recover Telescope Mid when it remains in given ObsState for long time
=======================================================================
The following table lists the steps to recover Telescope Mid when it is stuck in one
of the intermediate ObsState (Example: RESOURCING, CONFIGURING).

The provided steps consist of command-line instructions that are executable from any Python
runtime environment/script.

Using Abort() & Restart() Command
---------------------------------
+-----------------------------------+------------------------------------------------------------------------+
| Scenario                          |               Steps to recover                                         |
+===================================+========================================================================+
| When Telescope Mid is stuck in    |- Using Subarray Node                                                   |
| one of the ObsStates while running|    - Create device proxy of subarray node                              |
|                                   |    - To recover Telescope Low stuck in RESOURCING from Subarray node, |
|                                   |      execute Abort() command followed by Restart() command.            |
|                                   |                                                                        |
|                                   |      - subarray_node = tango.DeviceProxy("ska_mid/tm_subarray_node/01")|
| + RESOURCING                      |      - subarray_node.Abort()                                           |
|                                   |      - subarray_node.Restart()                                         |
| + CONFIGURING                     |                                                                        |
+-----------------------------------+------------------------------------------------------------------------+   

Using ReleaseAllResources() Command
------------------------------------

When Telescope Mid AssignResources() command is executed on some of the devices successfully and the Telescope subarray goes into
RESOURCING due to one of the devices getting stuck in RESOURCING.
So instead of doing Abort and Restart, invoke ReleaseAllResources() command on the subarray where the ObsState
is IDLE.
On the device where the ObsState is RESOURCING, invoke Abort() command followed by Restart() command.

+-----------------------------------+------------------------------------------------------------------------+
| Scenario                          |               Steps to recover                                         |
+===================================+========================================================================+
| When Telescope Mid is stuck in    | - Create device proxy of cspleafnode, sdpleafnode, and mccsleafnode    |
| RESOURCING                        | - Check the ObsState of each device                                    |
|                                   | - If the ObsState of the device is IDLE, invoke ReleaseAllResources()  |
|                                   |   command on that device. For example:                                |
|                                   | -  cspleafnode_proxy =                                                 |
|                                   |    tango.DeviceProxy("ska_mid/tm_leaf_node/csp_subarray01")            |
|                                   | - To check the ObsState of cspleafnode, execute                        |
|                                   |   `cspleafnode_proxy.obsState`                                         |
|                                   | - To release resources of the device, execute                          |
|                                   |   `cspleafnode_proxy.ReleaseAllResources()`                            |
|                                   | - To recover the device in RESOURCING ObsState, execute                |
|                                   |   Abort() command followed by Restart() command                        |
|                                   | - `stuck_device_proxy.Abort()`                                         |
|                                   | - `stuck_device_proxy.Restart()`                                       |
+-----------------------------------+------------------------------------------------------------------------+

Telescope Mid in FAULT ObsState
-------------------------------
+-----------------------------------+------------------------------------------------------------------------+
| Scenario                          |               Steps to recover                                         |
+===================================+========================================================================+
| When Telescope Mid is stuck in    |- Using Subarray Node                                                   |
| FAULT ObsState                    |    - Create device proxy of subarray node                              |
|                                   |    - To recover Telescope Low stuck in FAULT from Subarray node,       |
|                                   |      execute the RESTART command.                                      |
|                                   |    - subarray_node = tango.DeviceProxy("ska_mid/tm_subarray_node/01")  |
|                                   |    - subarray_node.Restart()                                           |
+-----------------------------------+------------------------------------------------------------------------+

