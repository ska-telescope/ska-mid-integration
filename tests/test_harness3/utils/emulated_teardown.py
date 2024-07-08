"""Utilities to tear down emulated components or a test harness."""

from ska_control_model import HealthState
from tango import DeviceProxy


def reset_delay(devices: list[DeviceProxy]) -> None:
    """Reset the delay of the device."""
    for device in devices:
        device.ResetDelay()


def reset_health_state(devices: list[DeviceProxy]) -> None:
    """Reset the health state of the device."""
    for device in devices:
        device.SetDirectHealthState(HealthState.UNKNOWN)


def clear_command_call(devices: list[DeviceProxy]) -> None:
    """Clear the command call of the device."""
    for device in devices:
        device.ClearCommandCallInfo()


def reset_transitions_data(devices: list[DeviceProxy]) -> None:
    """Reset the transition data of the device."""
    for device in devices:
        device.ResetTransitions()
