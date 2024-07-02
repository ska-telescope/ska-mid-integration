"""A wrapper for TMC and all integration tests sub-components."""

import json
import logging
import time
from typing import Tuple

from ska_control_model import ObsState, ResultCode
from ska_ser_logging import configure_logging

from tests.test_harness3.constant import (
    device_dict,  # TODO: find a way to handle this dependency
)
from tests.test_harness3.constant import DEFAULT_DISH_VCC_CONFIG
from tests.test_harness3.helpers import generate_eb_pb_ids
from tests.test_harness3.telescope_actions.central_node.move_to_off import (
    MoveToOff,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.common_utils import JsonFactory
from tests.test_harness3.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_load_dish_cfg,
    sync_release_resources,
    sync_restart,
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
    def central_node(self):
        """The central node Tango device proxy."""
        return self._telescope.tmc.central_node
    
    @property
    def csp_master_leaf_node(self):
        """The CSP master leaf node Tango device proxy."""
        return self._telescope.tmc.csp_master_leaf_node
    
    @property
    def sdp_master_leaf_node(self):
        """The SDP master leaf node Tango device proxy."""
        return self._telescope.tmc.sdp_master_leaf_node

    # -----------------------------------------------------------
    # SUB-ARRAY ACTIONS

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """This method creates subarray devices for the requested subarray
        id"""
        # TODO: separate in a TelescopeAction
        # TODO: this is something that should stay in TMCSubarrayFacade
        self._telescope.sdp.set_subarray_id(requested_subarray_id)
        self._telescope.csp.set_subarray_id(requested_subarray_id)
        self._telescope.tmc.set_subarray_id(requested_subarray_id)

    @sync_abort(device_dict=device_dict)
    def subarray_abort(self) -> Tuple[ResultCode, str]:
        """Invoke Abort command on subarray Node"""
        # TODO: separate in a TelescopeAction
        # TODO: this is something that should stay in TMCSubarrayFacade
        return self._telescope.tmc.subarray_abort()

    @sync_restart(device_dict=device_dict)
    def subarray_restart(self) -> Tuple[ResultCode, str]:
        """Invoke Restart command on subarray Node"""
        # TODO: separate in a TelescopeAction
        # TODO: this is something that should stay in TMCSubarrayFacade
        return self._telescope.tmc.subarray_restart()

    # -----------------------------------------------------------
    # CENTRAL NODE ACTIONS

    def load_dish_vcc_configuration(
        self, dish_vcc_config: str
    ) -> Tuple[ResultCode, str]:
        """Invoke LoadDishCfg command on central Node
        :param dish_vcc_config: Dish vcc configuration json string
        """
        # TODO: separate in a TelescopeAction
        result, message = self._telescope.tmc.central_node.LoadDishCfg(
            dish_vcc_config
        )
        return result, message

    def perform_action(
        self, command_name: str, input_json: str
    ) -> Tuple[ResultCode, str]:
        """Execute provided command on centralnode
        Args:
            command_name (str): Name of command to execute
            input_json (str): Json send as input to execute command
        """
        # TODO: separate in a TelescopeAction
        result, message = self._telescope.tmc.central_node.command_inout(
            command_name, input_json
        )
        return result, message

    # RESOURCE RELATED COMMANDS
    # (still actions on CentralNode!)

    @sync_assign_resources(device_dict=device_dict)
    def store_resources(self, assign_json: str) -> Tuple[ResultCode, str]:
        """Invoke Assign Resource command on central Node
        Args:
            assign_json (str): Assign resource input json
        """
        # TODO: separate in a TelescopeAction
        input_json = json.loads(assign_json)
        generate_eb_pb_ids(input_json)
        result, message = self._telescope.tmc.central_node.AssignResources(
            json.dumps(input_json)
        )
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    @sync_release_resources(device_dict=device_dict, timeout=500)
    def invoke_release_resources(
        self, input_string: str
    ) -> Tuple[ResultCode, str]:
        """Invoke Release Resource command on central Node
        Args:
            input_string (str): Release resource input json
        """
        # TODO: separate in a TelescopeAction
        time.sleep(3)

        result, message = self._telescope.tmc.central_node.ReleaseResources(
            input_string
        )
        return result, message

    # -----------------------------------------------------------
    # TEARDOWN

    # NOTE: used a lot in fixtures
    def tear_down(self) -> None:
        """Handle Tear down of central Node"""
        # TODO: separate in a TelescopeAction

        # NOTE: temporarily moved here because of synchronization
        Subarray_node_obsstate = self._telescope.tmc.subarray_node.obsState
        LOGGER.info(
            f"Calling tear down for CentralNode for SubarrayNode's \
                {Subarray_node_obsstate} obsstate."
        )

        if self._telescope.tmc.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling Release Resource on centralnode")
            json_factory = JsonFactory()
            release_input = json_factory.create_centralnode_configuration(
                "release_resources_mid"
            )
            self.invoke_release_resources(release_input)
        elif self._telescope.tmc.subarray_node.obsState in [
            ObsState.RESOURCING,
            ObsState.SCANNING,
            ObsState.CONFIGURING,
            ObsState.READY,
            ObsState.IDLE,
        ]:
            LOGGER.info("Calling Abort and Restart on SubarrayNode")
            self.subarray_abort()
            self.subarray_restart()
        elif self._telescope.tmc.subarray_node.obsState == ObsState.ABORTED:
            self.subarray_restart()

        # NOTE: temporarily moved here because of synchronization
        if self._telescope.tmc.telescope_state != "OFF":
            MoveToOff(self._telescope).execute()

        # reset HealthState.UNKNOWN in emulated devices
        # reset command calls and transitions in emulated devices
        self._telescope.csp.tear_down()
        self._telescope.sdp.tear_down()
        self._telescope.dishes.tear_down()

        # if source dish vcc config is empty or not matching with default
        # dish vcc then load default dish vcc config
        # CSP_SIMULATION_ENABLED condition will be removed after testing
        # with real csp
        if (
            not self._telescope.tmc.csp_master_leaf_node.sourceDishVccConfig
            or json.loads(
                self._telescope.tmc.csp_master_leaf_node.sourceDishVccConfig
            )
            != DEFAULT_DISH_VCC_CONFIG
        ):
            self._load_default_dish_vcc_config()

    @sync_load_dish_cfg(device_dict=device_dict)
    def _load_default_dish_vcc_config(self):
        """Load Default Dish Vcc config"""
        result, message = self.load_dish_vcc_configuration(
            json.dumps(DEFAULT_DISH_VCC_CONFIG)
        )
        return result, message

    # -----------------------------------------------------------
    # CURRENTLY UNUSED (maybe)

    # # NOTE: maybe never used, both internally and externally
    # def set_values_on_device(
    #     self, subarray_state: DevState,
    #     device_list, dish_mode: DishMode = None
    # ):
    #     """Set Device to ON"""
    #     for device in device_list:
    #         device_proxy = DeviceProxy(device)
    #         device_proxy.SetDirectState(subarray_state)

    #     # If Dish master provided then set it to standby
    #     if self.dish_master_list and dish_mode:
    #         for device in self.dish_master_list:
    #             device.SetDirectDishMode(dish_mode)

    # # NOTE: maybe never used, both internally and externally
    # def set_values_with_sdp_dish_mocks(
    #     self, subarray_state: DevState, dish_mode: DishMode
    # ) -> None:
    #     """
    #     A method to set values on mock SDP and Dish devices.
    #     Args:
    #         subarray_state: DevState - subarray state value for
    #                                 SDP Subarray
    #         dish_mode: DishMode - dish mode value for Dish Masters
    #     """
    #     # device_to_on_list = [self.subarray_devices.get("sdp_subarray")]
    #     device_to_on_list = [self._telescope.sdp.sdp_subarray]

    #     for device in device_to_on_list:
    #         device_proxy = DeviceProxy(device)
    #         device_proxy.SetDirectState(subarray_state)

    #     # If Dish master provided then set it to standby
    #     if self.dish_master_list:
    #         for device in self.dish_master_list:
    #             device.SetDirectDishMode(dish_mode)

    # # NOTE: maybe never used, both internally and externally
    # def _reset_sys_param_and_k_value(self) -> None:
    #     """Reset sysParam and sourceSysParam attribute of csp master
    #     reset kValue of Dish master
    #     """
    #     # NOTE: aren't those two IF conditions the same?
    #     # Should they instead be:
    #     # if emulation_configuration.dish:
    #     #     ...
    #     # if emulation_configuration.csp:
    #     #     ...

    #     # if (
    #     #     SIMULATED_DEVICES_DICT["csp_and_dish"]
    #     #     or SIMULATED_DEVICES_DICT["all_mocks"]
    #     # ):
    #     if (
    #         emulation_configuration.csp and emulation_configuration.dish
    #     ) or emulation_configuration.all_emulated():
    #         for mock_device in self.dish_master_list:
    #             mock_device.SetKValue(0)

    #     # if (
    #     #     SIMULATED_DEVICES_DICT["csp_and_dish"]
    #     #     or SIMULATED_DEVICES_DICT["all_mocks"]
    #     # ):
    #     if (
    #         emulation_configuration.csp and emulation_configuration.dish
    #     ) or emulation_configuration.all_emulated():
    #         self._telescope.csp_master.ResetSysParams()
