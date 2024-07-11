"""A wrapper for TMC and all integration tests sub-components."""

import logging
from typing import Tuple

from ska_control_model import ResultCode
from ska_ser_logging import configure_logging
from tango import DeviceProxy, DevState

from tests.test_harness3.constant import (
    device_dict,  # TODO: find a way to handle this dependency
)
from tests.test_harness3.telescope_actions.central_node.central_node_load_dish_config import (  # pylint: disable=line-too-long # noqa E501
    CentralNodeLoadDishConfig,
)
from tests.test_harness3.telescope_actions.central_node.central_node_perform_action import (  # pylint: disable=line-too-long # noqa E501
    CentralNodePerformAction,
)
from tests.test_harness3.telescope_actions.central_node.central_node_release_resources import (  # pylint: disable=line-too-long # noqa E501
    CentralNodeReleaseResources,
)
from tests.test_harness3.telescope_actions.central_node.central_node_store_resources import (  # pylint: disable=line-too-long # noqa E501
    CentralNodeStoreResources,
)
from tests.test_harness3.telescope_actions.central_node.move_to_off import (
    MoveToOff,
)
from tests.test_harness3.telescope_actions.central_node.move_to_on import (
    MoveToOn,
)
from tests.test_harness3.telescope_actions.central_node.set_standby import (
    SetStandby,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.wait_helpers import Waiter

# SIMULATED_DEVICES_DICT, wait_csp_master_off,

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TMCCentralNodeFacade:  # pylint: disable=too-many-public-methods
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Mid CentralNode,
    defined by the SKA Control Model.
    TODO: re-write"""

    def __init__(self, telescope: TelescopeWrapper) -> None:
        self._telescope = telescope

        # NOTE: todo: remove this bad dependency
        device_dict["cbf_subarray1"] = "mid_csp_cbf/sub_elt/subarray_01"
        device_dict["cbf_controller"] = "mid_csp_cbf/sub_elt/controller"
        device_dict[
            "dish_master_list"
        ] = self._telescope.dishes.dish_master_list
        device_dict[
            "dish_leaf_node_list"
        ] = self._telescope.tmc.dish_leaf_node_list
        self.wait = Waiter(**device_dict)

    # -----------------------------------------------------------
    # CENTRAL NODE DEVICES

    @property
    def central_node(self) -> DeviceProxy:
        """The central node Tango device proxy."""
        return self._telescope.tmc.central_node

    @property
    def csp_master_leaf_node(self) -> DeviceProxy:
        """The CSP master leaf node Tango device proxy."""
        return self._telescope.tmc.csp_master_leaf_node

    @property
    def sdp_master_leaf_node(self) -> DeviceProxy:
        """The SDP master leaf node Tango device proxy."""
        return self._telescope.tmc.sdp_master_leaf_node

    # -----------------------------------------------------------
    # CENTRAL NODE PROPERTIES

    # NOTE: same as for `state`
    @property
    def telescope_state(self) -> DevState:
        """Get telescope state representing overall state of telescope."""
        self._telescope.tmc.telescope_state

    @telescope_state.setter
    def telescope_state(self, value: DevState) -> None:
        """Set telescope state representing overall state of telescope."""
        self._telescope.tmc.telescope_state = value

    # -----------------------------------------------------------
    # STATE ACTIONS

    def move_to_on(self, wait_termination_condition: bool = True) -> None:
        """Move the telescope to ON state."""
        action = MoveToOn()
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    def move_to_off(self, wait_termination_condition: bool = True) -> None:
        """Move the telescope to OFF state."""
        action = MoveToOff()
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    def set_standby(self, wait_termination_condition: bool = True) -> None:
        """Set the telescope to STANDBY state."""
        action = SetStandby()
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    # -----------------------------------------------------------
    # CENTRAL NODE ACTIONS

    def load_dish_vcc_configuration(
        self, dish_vcc_config: str, wait_termination_condition: bool = True
    ) -> Tuple[ResultCode, str]:
        """Invoke LoadDishCfg command on central Node
        :param dish_vcc_config: Dish vcc configuration json string
        """
        action = CentralNodeLoadDishConfig(dish_vcc_config)
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    def perform_action(
        self,
        command_name: str,
        input_json: str,
        wait_termination_condition: bool = True,
    ) -> Tuple[ResultCode, str]:
        """Execute provided command on centralnode
        Args:
            command_name (str): Name of command to execute
            input_json (str): Json send as input to execute command
        """
        action = CentralNodePerformAction(command_name, input_json)
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    # @sync_assign_resources(device_dict=device_dict)
    def store_resources(
        self, assign_json: str, wait_termination_condition: bool = True
    ) -> Tuple[ResultCode, str]:
        """Invoke Assign Resource command on central Node

        :param assign_json: Assign resource input json
        """
        action = CentralNodeStoreResources(assign_json)
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()

    # @sync_release_resources(device_dict=device_dict, timeout=500)
    def invoke_release_resources(
        self, input_string: str, wait_termination_condition: bool = True
    ) -> Tuple[ResultCode, str]:
        """Invoke Release Resource command on central Node

        :param input_string (str): Release resource input json
        """
        action = CentralNodeReleaseResources(input_string)
        action.set_termination_condition_policy(wait_termination_condition)
        action.execute()
