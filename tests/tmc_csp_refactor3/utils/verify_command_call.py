"""Verify a certain Tango device receives a certain command call."""


import tango

# NOTE: probably this will require a sort of TangoCommandTracer class (?)


def verify_device_received_command(
    device: tango.DeviceProxy,
    command_name: str,
) -> None:
    """Verify a certain Tango device receives a certain command call.

    If everything is correct, the command should be executed without errors.
    Otherwise, an assertion error will be raised.

    :param device: The Tango device to be verified.
    :param command_name: The command to be verified.

    :raise AssertionError: If the command has not been called on the given
        device (withing a certain timeout).
    """
