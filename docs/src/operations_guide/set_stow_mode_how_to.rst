.. _`Applying SetStowMode Through TMC`:

=================================================
Steps to apply Stow mode on Dish(es) Through TMC
=================================================

Overview
--------

TMC Mid supports manual and auto stow functionality starting from version 1.16.0.

This document describes ways to apply the stow mode to dishes using TMC.


Central Node
------------

The **SetStowMode** command is available on the TMC and is used to apply the stow mode to specified dishes.

TMC also supports auto stow functionality.
For details on auto stow and manual stow, please refer to |TMC AutoStow Workflow|_.

.. |TMC AutoStow Workflow| replace:: **TMC Stow Workflow**
.. _TMC AutoStow Workflow: https://confluence.skatelescope.org/x/GqDDFQ

Dish Leaf Node
--------------

To work auto stow mode correctly, please update below properties under dish leaf node section of values.yaml file in TMC.

#. **WeatherStationDeviceNames** : TRL's of the weather stations.
#. **MaxAllowedWindspeed** : Maximum permissible wind speed in m/s before triggering dish stow. Default value is 13.5 m/s.
#. **MaxAllowedOpsWindspeed** : Maximum permissible ops wind speed in m/s before triggering dish stow. Default value is 10 m/s.
#. **MaxAllowedGustWindspeed** : Maximum permissible gust wind speed in m/s before triggering dish stow. Default value is 20 m/s.
#. **MaxAllowedWindspeedDifference** : Maximum permissible wind speed difference in m/s before triggering dish stow. Default value is 4.5 m/s.
#. **WindspeedMeasurementTimeWindow** : Time window (in seconds) over which wind speed measurements are evaluated. Default is 1000.
#. **GustWindspeedMeasurementTimeWindow** : Time window (in seconds) used to assess gust wind speed. Default is 3.
#. **MeanWindspeedTimeWindow** : Time window (in seconds) for calculating the mean wind speed. Default is 600.
#. **MaxAllowedOpsMeanWindspeedMeasurementTimeWindow** : Time window (in seconds) for evaluating the maximum allowed operational mean wind speed. Default is 600.
#. **MaxTemperatureThreshold** : Maximum allowable temperature (°C) before protective action is triggered. Default is 40.
#. **MinTemperatureThreshold** :  Minimum allowable temperature (°C) before protective action is triggered. Default is -5.
#. **TimeDelta** : Maximum allowed time difference (in seconds) between successive measurements. Default is 1000.
#. **TemperatureDelta** : Maximum permitted temperature variation (°C) within the defined time window. Default is 10.
#. **EnableAutoStow**: Flag to enable or disable automatic stow. Default is true.

**Note:** While configuring above values for dish leaf node, please also update below property for **Dish pointing** device of dish leaf node:

#. **WeatherStationDeviceNames** : TRL's of the weather stations.

Example: SetStowMode command(manual execution)

.. code-block:: python

    central_node_proxy = tango.DeviceProxy("mid-tmc/central-node/0")

    # To specified dishes
    central_node_proxy.SetStowMode(json.dumps(['SKA001', 'SKA036', 'SKA077']))

    # To all dishes
    central_node_proxy.SetStowMode(json.dumps(['ALL']))






