"""Wrapper for subarray node."""

import logging

from ska_ser_logging import configure_logging

from tests.test_harness3.telescope_actions.subarray.force_change_of_obs_state import (  # pylint: disable=line-too-long # noqa: E501
    ForceChangeOfObsState,
)
from tests.test_harness3.telescope_actions.subarray.set_subarray_id import (
    SetSubarrayId,
)
from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_assign_resources import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayAssignResources,
)
from tests.test_harness3.telescope_actions.subarray.subarray_configure import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayConfigure,
)
from tests.test_harness3.telescope_actions.subarray.subarray_end_observation import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayEndObservation,
)
from tests.test_harness3.telescope_actions.subarray.subarray_end_scan import (
    SubarrayEndScan,
)
from tests.test_harness3.telescope_actions.subarray.subarray_execute_transition import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayExecuteTransition,
)
from tests.test_harness3.telescope_actions.subarray.subarray_five_point_calibration_scan import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayFivePointCalibrationScan,
)
from tests.test_harness3.telescope_actions.subarray.subarray_move_to_off import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayMoveToOff,
)
from tests.test_harness3.telescope_actions.subarray.subarray_move_to_on import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayMoveToOn,
)
from tests.test_harness3.telescope_actions.subarray.subarray_release_all_resources import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayReleaseAllResources,
)
from tests.test_harness3.telescope_actions.subarray.subarray_restart import (
    SubarrayRestart,
)
from tests.test_harness3.telescope_actions.subarray.subarray_scan import (
    SubarrayScan,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TMCSubarrayNodeFacade:
    """Subarray Node class which implement methods required for test cases
    to test subarray node.
    """

    def __init__(self, telescope: TelescopeWrapper) -> None:
        """Initialize the SubarrayNodeWrapper."""
        self._telescope = telescope

    # -----------------------------------------------------------
    # SUBARRAY DEVICES

    @property
    def dish_leaf_node_list(self):
        """Return Dish Leaf Node List"""
        return self._telescope.tmc.dish_leaf_node_list[:2]

    @property
    def subarray_node(self):
        """Return Subarray Node Proxy"""
        return self._telescope.tmc.subarray_node

    @property
    def csp_master_leaf_node(self):
        """Return CSP Master Leaf Node Proxy"""
        return self._telescope.tmc.csp_master_leaf_node

    @property
    def sdp_master_leaf_node(self):
        """Return SDP Master Leaf Node Proxy"""
        return self._telescope.tmc.sdp_master_leaf_node

    # -----------------------------------------------------------
    # SUBARRAY PROPERTIES

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """Create subarray devices for the requested subarray."""
        SetSubarrayId(requested_subarray_id).execute()

    def move_to_on(self):
        """Move subarray to ON state.

        :return: result, message"""
        return SubarrayMoveToOn().execute()

    def move_to_off(self):
        """Move Subarray to OFF state.

        :return: result, message"""
        return SubarrayMoveToOff().execute()

    # -----------------------------------------------------------
    # Obs-state machine transitions

    # @sync_configure(device_dict=device_dict)
    def configure(self, input_string: str):
        """Invoke configure command on subarray Node.

        :param input_string: input string as json
        :return: result, message
        """
        return SubarrayConfigure(input_string).execute()

    # @sync_end(device_dict=device_dict)
    def end_observation(self):
        """Invoke End command on subarray Node.

        :return: result, message
        """
        return SubarrayEndObservation().execute()

    # @sync_endscan(device_dict=device_dict)
    def end_scan(self):
        """Invoke EndScan command on subarray Node.

        :return: result, message
        """
        return SubarrayEndScan().execute()

    def scan(self, input_string, wait_termination_condition: bool = True):
        """Invoke Scan command on subarray Node.

        :return: result, message
        """
        return SubarrayScan(input_string).execute(
            wait_termination_condition=wait_termination_condition
        )

    # @sync_abort(device_dict=device_dict)
    def abort(self):
        """Invoke Abort command on subarray Node.

        :return: result, message
        """
        return SubarrayAbort().execute()

    # @sync_restart(device_dict=device_dict)
    def restart(self):
        """Invoke Restart command on subarray Node.

        :return: result, message
        """
        return SubarrayRestart().execute()

    # @sync_assign_resources(device_dict)
    def assign_resources(self, assign_json: str):
        """Invoke Assign Resource command on subarray Node

        :param assign_json: Assign resource input json
        :return: result, message
        """
        return SubarrayAssignResources(assign_json).execute()

    # @sync_release_resources(device_dict)
    def release_all_resources(
        self,
    ):
        """Invoke Release Resource command on subarray Node.

        :return: result, message
        """
        return SubarrayReleaseAllResources().execute()

    # -----------------------------------------------------------
    # Generic transitions

    def execute_transition(self, command_name: str, argin=None):
        """Execute provided command on subarray

        :param command_name: Name of command to execute
        :param argin: Input argument for command

        :return: result, message
        """
        return SubarrayExecuteTransition(command_name, argin).execute()

    def force_change_of_obs_state(
        self,
        dest_state_name: str,
        assign_input_json: str | None = None,
        configure_input_json: str | None = None,
        scan_input_json: str | None = None,
        wait_termination_condition: bool = True,
    ) -> None:
        """Force SubarrayNode obsState to provided obsState.

        :param dest_state_name: Name of the destination obsState.
            TODO: replace with enum
        :param assign_input_json: Assign input json. If you leave it as None,
            it will use the default assign input json.
        :param configure_input_json: Configure input json. If you leave
            it as None, it will use the default configure input json.
        :param scan_input_json: Scan input json. If you leave it as None,
            it will use the default scan input json.
        """
        ForceChangeOfObsState(
            dest_state_name,
            assign_input_json,
            configure_input_json,
            scan_input_json,
        ).execute(wait_termination_condition=wait_termination_condition)

    def execute_five_point_calibration_scan(
        self,
        partial_configure_jsons: list[str],
        scan_jsons: list[str],
        event_recorder,
        command_input_factory,
    ) -> None:
        """Perform a five point calibration scan on Subarray Node using the
        partial configuration jsons and scan jsons provided as inputs.

        :param partial_configure_jsons: Partial configuration json file names
        :param scan_jsons: Scan json file names
        """
        SubarrayFivePointCalibrationScan(
            partial_configure_jsons,
            scan_jsons,
            event_recorder,
            command_input_factory,
        ).execute()
