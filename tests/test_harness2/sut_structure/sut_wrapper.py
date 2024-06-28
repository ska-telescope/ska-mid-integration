"""A wrapper for TMC and all integration tests sub-components."""

import json
import logging
from typing import Tuple

from ska_control_model import ObsState, ResultCode
from ska_ser_logging import configure_logging

from tests.test_harness2.constant import (
    device_dict,  # TODO: find a way to handle this dependency
)
from tests.test_harness2.constant import DEFAULT_DISH_VCC_CONFIG
from tests.test_harness2.sut_structure.csp_wrapper import CSPWrapper
from tests.test_harness2.sut_structure.dishes_wrapper import DishesWrapper
from tests.test_harness2.sut_structure.sdp_wrapper import SDPWrapper
from tests.test_harness2.sut_structure.sut_action import SUTAction
from tests.test_harness2.sut_structure.tmc_wrapper import TMCWrapper
from tests.test_harness2.utils.common_utils import JsonFactory
from tests.test_harness2.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_load_dish_cfg,
    sync_release_resources,
    sync_restart,
)
from tests.test_harness2.utils.wait_helpers import Waiter

# SIMULATED_DEVICES_DICT, wait_csp_master_off,

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TelescopeWrapper:  # pylint: disable=too-many-public-methods
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Mid CentralNode,
    defined by the SKA Control Model."""

    def __init__(
        self,
        tmc_wrapper: TMCWrapper,
        sdp_wrapper: SDPWrapper,
        csp_wrapper: CSPWrapper,
        dishes_wrapper: DishesWrapper,
        move_to_off_action: SUTAction,
    ) -> None:
        super().__init__()

        self.tmc = tmc_wrapper
        self.sdp = sdp_wrapper
        self.csp = csp_wrapper
        self.dishes = dishes_wrapper

        self._move_to_off_action = move_to_off_action

        # NOTE: todo: remove this bad dependency
        device_dict["cbf_subarray1"] = "mid_csp_cbf/sub_elt/subarray_01"
        device_dict["cbf_controller"] = "mid_csp_cbf/sub_elt/controller"
        device_dict["dish_master_list"] = self.dishes.dish_master_list
        device_dict["dish_leaf_node_list"] = self.tmc.dish_leaf_node_list
        self.wait = Waiter(**device_dict)

    def execute_action(self, action: SUTAction):
        """Execute an action on the SUT.

        :param action: The action to execute.

        :raises TimeoutError: If the expected outcome does not occur
            within a timeout.
        """
        action.set_sut_components(self.tmc, self.csp, self.sdp, self.dishes)
        action.execute()

    # -----------------------------------------------------------
    # SUB-ARRAY ACTIONS

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """This method creates subarray devices for the requested subarray
        id"""
        self.sdp.set_subarray_id(requested_subarray_id)
        self.csp.set_subarray_id(requested_subarray_id)
        self.tmc.set_subarray_id(requested_subarray_id)

    @sync_abort(device_dict=device_dict)
    def subarray_abort(self) -> Tuple[ResultCode, str]:
        """Invoke Abort command on subarray Node"""
        return self.tmc.subarray_abort()

    @sync_restart(device_dict=device_dict)
    def subarray_restart(self) -> Tuple[ResultCode, str]:
        """Invoke Restart command on subarray Node"""
        return self.tmc.subarray_restart()

    # -----------------------------------------------------------
    # CENTRAL NODE ACTIONS

    def load_dish_vcc_configuration(
        self, dish_vcc_config: str
    ) -> Tuple[ResultCode, str]:
        """Invoke LoadDishCfg command on central Node
        :param dish_vcc_config: Dish vcc configuration json string
        """
        return self.tmc.load_dish_vcc_configuration(dish_vcc_config)

    def perform_action(
        self, command_name: str, input_json: str
    ) -> Tuple[ResultCode, str]:
        """Execute provided command on centralnode
        Args:
            command_name (str): Name of command to execute
            input_json (str): Json send as input to execute command
        """
        return self.tmc.perform_action(command_name, input_json)

    # RESOURCE RELATED COMMANDS
    # (still actions on CentralNode!)

    @sync_assign_resources(device_dict=device_dict)
    def store_resources(self, assign_json: str) -> Tuple[ResultCode, str]:
        """Invoke Assign Resource command on central Node
        Args:
            assign_json (str): Assign resource input json
        """
        return self.tmc.store_resources(assign_json)

    @sync_release_resources(device_dict=device_dict, timeout=500)
    def invoke_release_resources(
        self, input_string: str
    ) -> Tuple[ResultCode, str]:
        """Invoke Release Resource command on central Node
        Args:
            input_string (str): Release resource input json
        """
        return self.tmc.invoke_release_resources(input_string)

    # -----------------------------------------------------------
    # TEARDOWN

    # NOTE: used a lot in fixtures
    def tear_down(self) -> None:
        """Handle Tear down of central Node"""
        # NOTE: temporarily moved here because of synchronization
        Subarray_node_obsstate = self.tmc.subarray_node.obsState
        LOGGER.info(
            f"Calling tear down for CentralNode for SubarrayNode's \
                {Subarray_node_obsstate} obsstate."
        )

        if self.tmc.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling Release Resource on centralnode")
            json_factory = JsonFactory()
            release_input = json_factory.create_centralnode_configuration(
                "release_resources_mid"
            )
            self.invoke_release_resources(release_input)
        elif self.tmc.subarray_node.obsState in [
            ObsState.RESOURCING,
            ObsState.SCANNING,
            ObsState.CONFIGURING,
            ObsState.READY,
            ObsState.IDLE,
        ]:
            LOGGER.info("Calling Abort and Restart on SubarrayNode")
            self.subarray_abort()
            self.subarray_restart()
        elif self.tmc.subarray_node.obsState == ObsState.ABORTED:
            self.subarray_restart()

        # NOTE: temporarily moved here because of synchronization
        if self.tmc.telescope_state != "OFF":
            self.execute_action(self._move_to_off_action)

        # reset HealthState.UNKNOWN in emulated devices
        # reset command calls and transitions in emulated devices
        self.csp.tear_down()
        self.sdp.tear_down()
        self.dishes.tear_down()

        # if source dish vcc config is empty or not matching with default
        # dish vcc then load default dish vcc config
        # CSP_SIMULATION_ENABLED condition will be removed after testing
        # with real csp
        if (
            not self.tmc.csp_master_leaf_node.sourceDishVccConfig
            or json.loads(self.tmc.csp_master_leaf_node.sourceDishVccConfig)
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
    #     device_to_on_list = [self.sdp.sdp_subarray]

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
    #         self.csp_master.ResetSysParams()
