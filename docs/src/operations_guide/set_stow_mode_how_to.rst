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

#. **weather_station_device_names** : TRL's of the weather stations.
#. **max_allowed_wind_speed** : Maximum permissible wind speed in m/s before triggering dish stow. Default value is 13.5 m/s.
#. **max_allowed_ops_wind_speed** : Maximum permissible ops wind speed in m/s before triggering dish stow. Default value is 10 m/s.
#. **max_allowed_gust_wind_speed** : Maximum permissible gust wind speed in m/s before triggering dish stow. Default value is 20 m/s.
#. **max_allowed_wind_speed_difference** : Maximum permissible wind speed difference in m/s before triggering dish stow. Default value is 4.5 m/s.
#. **wind_speed_measurement_time_window** : Time window (in seconds) over which wind speed measurements are evaluated. Default is 1000.
#. **gust_wind_speed_measurement_time_window** : Time window (in seconds) used to assess gust wind speed. Default is 3.
#. **mean_wind_speed_measurement_time_window** : Time window (in seconds) for calculating the mean wind speed. Default is 600.
#. **max_allowed_ops_mean_wind_speed_measurement_time_window** : Time window (in seconds) for evaluating the maximum allowed operational mean wind speed. Default is 600.
#. **max_temp_threshold** : Maximum allowable temperature (°C) before protective action is triggered. Default is 40.
#. **min_temp_threshold** :  Minimum allowable temperature (°C) before protective action is triggered. Default is -5.
#. **time_delta** : Maximum allowed time difference (in seconds) between successive measurements. Default is 1000.
#. **temp_delta** : Maximum permitted temperature variation (°C) within the defined time window. Default is 10.
#. **enable_auto_stow**: Flag to enable or disable automatic stow. Default is true.

**Note:** While configuring above values for dish leaf node, please also update below property for **Dish pointing** device of dish leaf node:

#. **weather_station_device_names** : TRL's of the weather stations.

**Caution:**
If the enable_auto_stow flag is set to true, the dish will automatically transition to stow position once the configured weather station criteria are met.

Additionally, if the weather station becomes unavailable, the dishes will also automatically stow as a safety measure.

This behavior can be disabled by setting:

.. code-block:: python
    enable_auto_stow = false


The enable_auto_stow parameter (and related values) can be configured:

During deployment, or

At runtime, using:

.. code-block:: python
    <device-proxy>.<parameter> = "value to be set"


Please ensure the flag is configured appropriately by setting the above mentioned values to avoid unintended automatic stow operations.

Example: SetStowMode command(manual execution)

.. code-block:: python

    central_node_proxy = tango.DeviceProxy("mid-tmc/central-node/0")

    # To specified dishes
    central_node_proxy.SetStowMode(json.dumps(['SKA001', 'SKA036', 'SKA077']))

    # To all dishes
    central_node_proxy.SetStowMode(json.dumps(['ALL']))






