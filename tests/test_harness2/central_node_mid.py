"""A wrapper for TMC and all integration tests sub-components."""

import json
import logging
from typing import Tuple

from ska_control_model import ObsState, ResultCode
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.test_harness2.constant import (
    device_dict,  # TODO: find a way to handle this dependency
)
from tests.test_harness2.constant import DEFAULT_DISH_VCC_CONFIG
from tests.test_harness2.sys_components.csp_wrapper import CSPWrapper
from tests.test_harness2.sys_components.dishes_wrapper import DishesWrapper
from tests.test_harness2.sys_components.sdp_wrapper import SDPWrapper
from tests.test_harness2.sys_components.tmc_wrapper import TMCWrapper
from tests.test_harness2.utils.common_utils import JsonFactory
from tests.test_harness2.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_load_dish_cfg,
    sync_release_resources,
    sync_restart,
    sync_set_to_off,
    sync_set_to_standby,
)
from tests.test_harness2.utils.wait_helpers import Waiter

# SIMULATED_DEVICES_DICT, wait_csp_master_off,

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class CentralNodeWrapperMid:  # pylint: disable=too-many-public-methods
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Mid CentralNode,
    defined by the SKA Control Model."""

    def __init__(
        self,
        tmc_wrapper: TMCWrapper,
        sdp_wrapper: SDPWrapper,
        csp_wrapper: CSPWrapper,
        dishes_wrapper: DishesWrapper,
    ) -> None:
        super().__init__()

        self.tmc = tmc_wrapper
        self.sdp = sdp_wrapper
        self.csp = csp_wrapper
        self.dishes = dishes_wrapper

        # NOTE: todo: remove this bad dependency
        device_dict["cbf_subarray1"] = "mid_csp_cbf/sub_elt/subarray_01"
        device_dict["cbf_controller"] = "mid_csp_cbf/sub_elt/controller"
        device_dict["dish_master_list"] = self.dish_master_list
        device_dict["dish_leaf_node_list"] = self.dish_leaf_node_list
        self.wait = Waiter(**device_dict)

    # -----------------------------------------------------------
    # REPLICATED DEVICES
    # TODO: change external references to those properties
    # ISSUE: it has to be done with updated test... better if
    # in just one quick and light MR

    # Central Node
    @property
    def central_node(self) -> DeviceProxy:
        """CentralNode device proxy"""
        return self.tmc.central_node

    @property
    def subarray_node(self) -> DeviceProxy:
        """SubarrayNode device proxy"""
        return self.tmc.subarray_node

    @property
    def csp_master_leaf_node(self) -> DeviceProxy:
        """CSP Master Leaf Node device proxy"""
        return self.tmc.csp_master_leaf_node

    @property
    def sdp_master_leaf_node(self) -> DeviceProxy:
        """SDP Master Leaf Node device proxy"""
        return self.tmc.sdp_master_leaf_node

    @property
    def dish_leaf_node_list(self) -> list[DeviceProxy]:
        """Dish Leaf Node device proxies as a list"""
        return self.tmc.dish_leaf_node_list

    @property
    def dish1_leaf_admin_dev_name(self) -> str:
        """Dish1 Leaf Admin device name"""
        return self.tmc.dish1_leaf_admin_dev_name

    @property
    def dish1_leaf_admin_dev_proxy(self) -> DeviceProxy:
        """Dish1 Leaf Admin device proxy"""
        return self.tmc.dish1_leaf_admin_dev_proxy

    #
    # SDP & CSP
    @property
    def sdp_master(self) -> DeviceProxy:
        """SDP Master device proxy"""
        return self.sdp.sdp_master

    @property
    def csp_master(self) -> DeviceProxy:
        """CSP Master device proxy"""
        return self.csp.csp_master

    @property
    def subarray_devices(self) -> dict[str, DeviceProxy]:
        """Subarray devices as a dict"""
        # subarray are relevant because they are the ones that obey with
        # the commands.
        return {
            #  this is internal to CSP
            # "csp_subarray": DeviceProxy(csp_subarray1),
            "csp_subarray": self.csp.csp_subarray,
            # this is internal to SDP
            # "sdp_subarray": DeviceProxy(sdp_subarray1),
            "sdp_subarray": self.sdp.sdp_subarray,
        }

    #
    # Dishes
    @property
    def dish_master_dict(self) -> dict[str, DeviceProxy]:
        """Dish Master device proxies as a dict."""
        return self.dishes.dish_master_dict

    @dish_master_dict.setter
    def dish_master_dict(self, value: dict[str, DeviceProxy]):
        self.dishes.dish_master_dict = value

    @property
    def dish_master_list(self) -> list[DeviceProxy]:
        """Dish Master device proxies as a list (sorted by key)."""
        return [
            self.dish_master_dict[key]
            for key in sorted(self.dish_master_dict.keys())
        ]

    @property
    def dish1_admin_dev_name(self) -> str:
        """Dish1 admin device name"""
        return self.dishes.dish1_admin_dev_name

    @property
    def dish1_admin_dev_proxy(self) -> DeviceProxy:
        """Dish1 admin device proxy"""
        return self.dishes.dish1_admin_dev_proxy

    # -----------------------------------------------------------
    # PROPERTIES ON CENTRAL NODE
    # Properties that are related to CentralNode. To get
    # them we interact with CentralNode device.

    # NOTE: `state` is never used
    @property
    def state(self) -> DevState:
        """TMC CentralNode operational state"""
        return self.tmc.state

    @state.setter
    def state(self, value: DevState):
        """Sets value for TMC CentralNode operational state

        Args:
            value (DevState): operational state value
        """
        self.tmc.state = value

    @property
    def IsDishVccConfigSet(self):
        """Return DishVccConfigSet flag"""
        return self.tmc.IsDishVccConfigSet

    @property
    def DishVccValidationStatus(self):
        """Current dish vcc validation status of central node"""
        return self.tmc.DishVccValidationStatus

    @property
    def telescope_health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        return self.tmc.telescope_health_state

    @telescope_health_state.setter
    def telescope_health_state(self, value: HealthState) -> None:
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self.tmc.telescope_health_state = value

    # NOTE: same as for `state`
    @property
    def telescope_state(self) -> DevState:
        """Telescope state representing overall state of telescope"""
        return self.tmc.telescope_state

    @telescope_state.setter
    def telescope_state(self, value: DevState) -> None:
        """Telescope state representing overall state of telescope

        Args:
            value (DevState): telescope state value
        """
        self.tmc.telescope_state = value

    # -----------------------------------------------------------
    # ON/OFF/STANDBY ACTIONS
    # They seem to be operations that move nodes State
    # ("hardware" state)

    def move_to_on(self) -> None:
        """
        A method to invoke TelescopeOn command to
        put telescope in ON state
        """
        LOGGER.info("Starting up the Telescope")
        # LOGGER.info(f"Received emulated devices: {emulation_configuration}")

        self.csp.move_to_on()
        self.tmc.move_central_node_to_on()

    @sync_set_to_off(device_dict=device_dict)
    def move_to_off(self) -> None:
        """
        A method to invoke TelescopeOff command to
        put telescope in OFF state
        """
        self.tmc.move_central_node_to_off()
        self.csp.move_to_off()

    @sync_set_to_standby(device_dict=device_dict)
    def set_standby(self) -> None:
        """
        A method to invoke TelescopeStandby command to
        put telescope in STANDBY state
        """
        LOGGER.info("Putting Telescope in Standby state")

        self.tmc.set_central_node_to_standby()
        self.csp.move_to_off()

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

        if self.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling Release Resource on centralnode")
            json_factory = JsonFactory()
            release_input = json_factory.create_centralnode_configuration(
                "release_resources_mid"
            )
            self.invoke_release_resources(release_input)
        elif self.subarray_node.obsState in [
            ObsState.RESOURCING,
            ObsState.SCANNING,
            ObsState.CONFIGURING,
            ObsState.READY,
            ObsState.IDLE,
        ]:
            LOGGER.info("Calling Abort and Restart on SubarrayNode")
            self.subarray_abort()
            self.subarray_restart()
        elif self.subarray_node.obsState == ObsState.ABORTED:
            self.subarray_restart()

        # NOTE: temporarily moved here because of synchronization
        if self.tmc.telescope_state != "OFF":
            self.move_to_off()

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
            not self.csp_master_leaf_node.sourceDishVccConfig
            or json.loads(self.csp_master_leaf_node.sourceDishVccConfig)
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
