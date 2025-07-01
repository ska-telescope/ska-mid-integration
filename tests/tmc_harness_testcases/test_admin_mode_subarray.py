"""Test the command not allowed when adminmode NOT_FITTED/OFFLINE"""
import time

import pytest
import tango
from pytest_bdd import parsers, scenario, then, when
from ska_control_model import AdminMode

from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_support.constant import csp_master, sdp_master

TIMEOUT = 100
SUBSYSTEM_DEVICES = {
    "cspcontroller": csp_master,
    "sdpcontroller": sdp_master,
}

@pytest.mark.batch2
@pytest.mark.SKA_mid
@scenario(
    "../features/check_cmd_not_allowed_adminmode.feature",
    "Command not allowed from SubarrayNode when subsystem adminmode "
    "is OFFLINE/NOT_FITTED",
)
def test_command_not_allowed():
    """
    Test case to verify command not allowed when adminMode OFFLINE/NOT_FITTED
    """


@when(
    parsers.parse(
        "the adminmode of subsystem subarray {subsystem} is {adminmode}"
    )
)
def set_admin_mode(subsystem, adminmode):
    """Set the admin mode of a given subsystem."""
    device_name = SUBSYSTEM_DEVICES[subsystem]
    proxy = tango.DeviceProxy(device_name)
    mode_enum = AdminMode[adminmode]
    proxy.adminMode = mode_enum
    time.sleep(0.1)
    # Optional: Assert adminMode is set
    assert proxy.adminMode == mode_enum


@when(parsers.parse("I invoke command {command} on subarraynode"))
def invoke_assignresources(
    command,
    subarray_node,
    command_input_factory,
):
    """Invokes command on TMC"""
    pytest.command_failed_exception = None

    try:
        if "Configure" in command:
            configure_input_json = prepare_json_args_for_commands(
                "configure_mid", command_input_factory
            )
            subarray_node.perform_action("Configure", configure_input_json)
        elif "Scan" in command:
            scan_input_json = prepare_json_args_for_commands(
                "scan_mid", command_input_factory
            )
            subarray_node.perform_action("Scan", scan_input_json)
        elif "EndScan" in command:
            subarray_node.perform_action("EndScan")
        elif "End" in command:
            subarray_node.perform_action("End")
        else:
            raise ValueError(f"Unsupported command: {command}")
    except (tango.DevFailed, RuntimeError, ValueError) as e:
        pytest.command_failed_exception = e


@then("the subarraynode rejects the command")
def subarraynode_rejects_command():
    """Assert the previously invoked command was rejected due to adminMode."""
    exc = getattr(pytest, "command_failed_exception", None)
    assert (
        exc is not None
    ), "Expected the command to be rejected, but it succeeded"

    expected_message = (
        "One or more subarray devices are in adminMode OFFLINE or NOT-FITTED"
    )

    # Handle both single and multiple DevError cases
    dev_errors = exc.args[0]
    if not isinstance(dev_errors, (list, tuple)):
        dev_errors = [dev_errors]

    error_messages = [err.desc for err in dev_errors]
    assert any(
        expected_message in msg for msg in error_messages
    ), f"Expected rejection message not found. Got: {error_messages}"
    # perform tear down
    for _, device in SUBSYSTEM_DEVICES.items():
        proxy = tango.DeviceProxy(device)
        proxy.adminMode = AdminMode.ONLINE
