"""Wrapper for subarray node."""

import logging

from ska_ser_logging import configure_logging

from tests.test_harness3.telescope_actions.subarray.force_change_of_obs_state import (  # pylint: disable=line-too-long # noqa: E501
    ForceChangeOfObsState,
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
    """A facade to TMC Subarray Node device and its actions.

    A facade to TMC sub-system, providing a simplified interface to the
    subarray node devices and their actions. It contains:

    - references to subarray node device,
    - references to leaf devices to interact with CSP and SDP subarrays,
    - an action to initialize the subarray setting the subarray ID,
    - actions to move the subarray to ON and OFF states,
    - actions to interact with the obs state of the subarray, making
      individual state changes (through command calls) or forcing the
      change of the obs state to a target state whatever the current state is,
    - various other actions (e.g., five point calibration scan).
    """

    def __init__(self, telescope: TelescopeWrapper) -> None:
        self._telescope = telescope

    # -----------------------------------------------------------
    # Subarray devices

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
    # Setter for initializing subarray

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """Create subarray devices for the requested subarray.

        :param requested_subarray_id: Subarray ID to set.
        """
        self._telescope.set_subarray_id(requested_subarray_id)

    # -----------------------------------------------------------
    # Actions over subarray telescope state

    def move_to_on(self, wait_termination_condition: bool = True):
        """Move subarray to ON state.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayMoveToOn()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    def move_to_off(self, wait_termination_condition: bool = True):
        """Move Subarray to OFF state.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayMoveToOff()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # -----------------------------------------------------------
    # Actions over subarray obs state

    # @sync_configure(device_dict=device_dict)
    def configure(
        self, input_string: str, wait_termination_condition: bool = True
    ):
        """Invoke configure command on subarray Node.

        :param input_string: input string as json.
        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayConfigure(input_string)
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_end(device_dict=device_dict)
    def end_observation(self, wait_termination_condition: bool = True):
        """Invoke End command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayEndObservation()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_endscan(device_dict=device_dict)
    def end_scan(self, wait_termination_condition: bool = True):
        """Invoke EndScan command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayEndScan()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    def scan(self, input_string, wait_termination_condition: bool = True):
        """Invoke Scan command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayScan(input_string)
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_abort(device_dict=device_dict)
    def abort(self, wait_termination_condition: bool = True):
        """Invoke Abort command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayAbort()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_restart(device_dict=device_dict)
    def restart(self, wait_termination_condition: bool = True):
        """Invoke Restart command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayRestart()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_assign_resources(device_dict)
    def assign_resources(
        self, assign_json: str, wait_termination_condition: bool = True
    ):
        """Invoke Assign Resource command on subarray Node

        :param assign_json: Assign resource input json.
        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayAssignResources(assign_json)
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # @sync_release_resources(device_dict)
    def release_all_resources(self, wait_termination_condition: bool = True):
        """Invoke Release Resource command on subarray Node.

        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayReleaseAllResources()
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

    # -----------------------------------------------------------
    # Generic ob-state transitions actions

    def execute_transition(
        self,
        command_name: str,
        argin=None,
        wait_termination_condition: bool = True,
    ):
        """Execute provided command on subarray

        :param command_name: Name of command to execute
        :param argin: Input argument for command
        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.

        :return: result, message
        """
        action = SubarrayExecuteTransition(command_name, argin)
        action.set_termination_condition_policy(wait_termination_condition)
        return action.execute()

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
        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.
        """
        action = ForceChangeOfObsState(
            dest_state_name,
            assign_input_json,
            configure_input_json,
            scan_input_json,
        )
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    def execute_five_point_calibration_scan(
        self,
        partial_configure_jsons: list[str],
        scan_jsons: list[str],
        command_input_factory,
        wait_termination_condition: bool = True,
    ) -> None:
        """Perform a five point calibration scan on Subarray Node using the
        partial configuration jsons and scan jsons provided as inputs.

        :param partial_configure_jsons: Partial configuration json file names
        :param scan_jsons: Scan json file names
        :param command_input_factory: Command input factory
        :param wait_termination_condition: set to False if you don't want to
            wait for the termination condition. By default the termination
            condition is waited.
        """
        action = SubarrayFivePointCalibrationScan(
            partial_configure_jsons,
            scan_jsons,
            command_input_factory,
        )
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()
