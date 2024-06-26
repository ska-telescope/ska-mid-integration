"""Wrapper for subarray node."""

import json
import logging

import msgpack
import msgpack_numpy
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.test_harness2.config.configuration_factory import (
    TestHarnessConfigurationFactory,
)
from tests.test_harness2.config.test_wrappers_configurations import (
    CSPConfiguration,
    DishesConfiguration,
    SDPConfiguration,
    TMCConfiguration,
)
from tests.test_harness2.constant import POINTING_OFFSETS, sdp_queue_connector
from tests.test_harness2.helpers import (  # SIMULATED_DEVICES_DICT,
    check_subarray_obs_state,
    generate_eb_pb_ids,
    prepare_json_args_for_commands,
)
from tests.test_harness2.utils.constant import ABORTED, IDLE, ON, READY
from tests.test_harness2.utils.enums import DishMode, SubarrayObsState
from tests.test_harness2.utils.obs_state_resetter import (
    ObsStateResetterFactory,
)
from tests.test_harness2.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_configure,
    sync_end,
    sync_endscan,
    sync_release_resources,
    sync_restart,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# get current configuration
configuration_factory = TestHarnessConfigurationFactory()

tmc_configuration: TMCConfiguration = (
    configuration_factory.get_TMC_configuration()
)
sdp_configuration: SDPConfiguration = (
    configuration_factory.get_SDP_configuration()
)
csp_configuration: CSPConfiguration = (
    configuration_factory.get_CSP_configuration()
)
dishes_configuration: DishesConfiguration = (
    configuration_factory.get_dish_configuration()
)

emulation_configuration = configuration_factory.emulation_configuration

# TODO: how can we remove this?
device_dict = {
    "sdp_subarray": sdp_configuration.sdp_subarray1_name,
    "csp_subarray": csp_configuration.csp_subarray1_name,
    "csp_master": csp_configuration.csp_master_name,
    "tmc_subarraynode": tmc_configuration.tmc_subarraynode1_name,
    "sdp_master": sdp_configuration.sdp_master_name,
    "centralnode": tmc_configuration.centralnode_name,
    "dish_master_list": [
        dishes_configuration.dish_master1_name,
        dishes_configuration.dish_master2_name,
    ],  # NOTE: why just two dishes?
    "csp_subarray_leaf_node": (
        tmc_configuration.tmc_csp_subarray_leaf_node_name
    ),
    "sdp_subarray_leaf_node": (
        tmc_configuration.tmc_sdp_subarray_leaf_node_name
    ),
}


# NOTE: another wrapper with a partially overlapping interface (?)
# TODO: after refactoring central node, choose what to do with this too
class SubarrayNodeWrapper:
    """Subarray Node class which implement methods required for test cases
    to test subarray node.
    """

    def __init__(self) -> None:
        """Initialize the SubarrayNodeWrapper."""
        # NOTE: similar public attributes and initialization procedure
        self.subarray_node = DeviceProxy(
            tmc_configuration.tmc_subarraynode1_name
        )
        self.subarray_node.set_timeout_millis(5000)

        self.csp_subarray_leaf_node = DeviceProxy(
            tmc_configuration.tmc_csp_subarray_leaf_node_name
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            tmc_configuration.tmc_sdp_subarray_leaf_node_name
        )
        self.dish_leaf_node_list = [
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node1_name),
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node2_name),
        ]
        for dish_leaf_node in self.dish_leaf_node_list:
            dish_leaf_node.set_timeout_millis(5000)

        self.dish_master_list = [
            DeviceProxy(dishes_configuration.dish_master1_name),
            DeviceProxy(dishes_configuration.dish_master2_name),
            DeviceProxy(dishes_configuration.dish_master3_name),
            DeviceProxy(dishes_configuration.dish_master4_name),
        ]

        self.subarray_devices = {
            "csp_subarray": DeviceProxy(csp_configuration.csp_subarray1_name),
            "sdp_subarray": DeviceProxy(sdp_configuration.sdp_subarray1_name),
        }

        self._state = DevState.OFF
        self.obs_state = SubarrayObsState.EMPTY
        # setup subarray
        self._setup()
        # Subarray state
        self.ON_STATE = ON
        self.IDLE_OBS_STATE = IDLE
        self.READY_OBS_STATE = READY
        self.ABORTED_OBS_STATE = ABORTED

    def _setup(self):
        """ """
        # if (
        #     SIMULATED_DEVICES_DICT["csp_and_dish"]
        #     or SIMULATED_DEVICES_DICT["all_mocks"]
        # ):
        if (
            emulation_configuration.csp and emulation_configuration.dish
        ) or emulation_configuration.all_emulated():
            for dish_master_proxy in self.dish_master_list:
                dish_master_proxy.SetDirectState(DevState.STANDBY)
                # Setting DishMode to STANDBY_FP
                dish_master_proxy.SetDirectDishMode(DishMode.STANDBY_FP)

    @property
    def state(self) -> DevState:
        """TMC SubarrayNode operational state"""
        self._state = Resource(tmc_configuration.tmc_subarraynode1_name).get(
            "State"
        )
        return self._state

    @state.setter
    def state(self, value):
        """Sets value for TMC subarrayNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    @property
    def obs_state(self):
        """TMC SubarrayNode observation state"""
        self._obs_state = Resource(
            tmc_configuration.tmc_subarraynode1_name
        ).get("obsState")
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value):
        """Sets value for TMC subarrayNode observation state

        Args:
            value (DevState): observation state value
        """
        self._obs_state = value

    @property
    def health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._health_state = Resource(
            tmc_configuration.tmc_subarraynode1_name
        ).get("healthState")
        return self._health_state

    @health_state.setter
    def health_state(self, value):
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self._health_state = value

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """This method creates subarray devices for the requested subarray
        id"""
        # NOTE: redundant method with central node (?)
        # (it actually contains a subset of the central node's method actions)
        subarray_id = str(requested_subarray_id).zfill(2)
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(f"mid-csp/subarray/{subarray_id}"),
            "sdp_subarray": DeviceProxy(f"mid-sdp/subarray/{subarray_id}"),
        }
        self.csp_subarray_leaf_node = DeviceProxy(
            f"ska_mid/tm_leaf_node/csp_subarray{subarray_id}"
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            f"ska_mid/tm_leaf_node/sdp_subarray{subarray_id}"
        )

    def move_to_on(
        self,
    ):
        """Move subarray to ON state."""
        if self.state != self.ON_STATE:
            Resource(
                tmc_configuration.tmc_subarraynode1_name
            ).assert_attribute("State").equals("OFF")
            result, message = self.subarray_node.On()
            LOGGER.info("Invoked ON on SubarrayNode")
            return (
                result,
                message,
            )
        # pylint says inconsistent-return-statements,
        # what should be returned here?
        return None

    def move_to_off(
        self,
    ):
        """Move Subarray to OFF state."""
        Resource(tmc_configuration.tmc_subarraynode1_name).assert_attribute(
            "State"
        ).equals("ON")
        result, message = self.subarray_node.Off()
        LOGGER.info("Invoked OFF on SubarrayNode")
        return (
            result,
            message,
        )

    @sync_configure(device_dict=device_dict)
    def store_configuration_data(self, input_string: str):
        """Invoke configure command on subarray Node
        Args:
            input_string (str): config input json
        Returns:
            (result, message): result, message tuple
        """
        result, message = self.subarray_node.Configure(input_string)
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    @sync_end(device_dict=device_dict)
    def end_observation(self):
        """Invoke End command on subarray Node."""
        result, message = self.subarray_node.End()
        LOGGER.info("Invoked End on SubarrayNode")
        return result, message

    @sync_endscan(device_dict=device_dict)
    def remove_scan_data(self):
        """Invoke EndScan command on subarray Node."""
        result, message = self.subarray_node.EndScan()
        LOGGER.info("Invoked EndScan on SubarrayNode")
        return result, message

    def store_scan_data(self, input_string):
        """Invoke Scan command on subarray Node."""
        result, message = self.subarray_node.Scan(input_string)
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    @sync_abort(device_dict=device_dict)
    def abort_subarray(self):
        """Invoke Abort command on subarray Node."""
        result, message = self.subarray_node.Abort()
        LOGGER.info("Invoked Abort on SubarrayNode")
        return result, message

    @sync_restart(device_dict=device_dict)
    def restart_subarray(self):  # pylint: disable=missing-function-docstring
        result, message = self.subarray_node.Restart()
        LOGGER.info("Invoked Restart on SubarrayNode")
        return result, message

    @sync_assign_resources(device_dict)
    def store_resources(self, assign_json: str):
        """Invoke Assign Resource command on subarray Node
        Args:
            assign_json (str): Assign resource input json
        """
        input_json = json.loads(assign_json)
        generate_eb_pb_ids(input_json)
        result, message = self.subarray_node.AssignResources(
            json.dumps(input_json)
        )
        LOGGER.info("Invoked AssignResources on SubarrayNode")
        return result, message

    @sync_release_resources(device_dict)
    def release_resources_subarray(
        self,
    ):
        """Invoke Release Resource command on subarray Node."""
        result, message = self.subarray_node.ReleaseAllResources()
        LOGGER.info("Invoked Release Resource on SubarrayNode")
        return result, message

    def execute_transition(self, command_name: str, argin=None):
        """Execute provided command on subarray
        Args:
            command_name (str): Name of command to execute
        """
        if command_name is not None:
            result, message = self.subarray_node.command_inout(
                command_name, argin
            )
            LOGGER.info(f"Invoked {command_name} on SubarrayNode")
            return (
                result,
                message,
            )
        # pylint says inconsistent-return-statements,
        # what should be returned here?
        return None

    def _reset_simulator_devices(self):
        """Reset Simulator devices to it's original state"""
        # NOTE: similar if-elif-else blocks too...
        # but here maybe we are working with subarrays,
        # instead of master devices (like in central node mid)

        # NOTE: similar to central node
        # _reset_health_state_for_mock_devices()
        # it calls SetDirectHealthState(HealthState.UNKNOWN)
        # to subarray devices instead of master devices

        sim_device_fqdn_list = []

        if emulation_configuration.csp:
            sim_device_fqdn_list.append(csp_configuration.csp_subarray1_name)

        if emulation_configuration.sdp:
            sim_device_fqdn_list.append(sdp_configuration.sdp_subarray1_name)

        for sim_device_fqdn in sim_device_fqdn_list:
            # NOTE: here self.etc are device names, not proxies...
            device = DeviceProxy(sim_device_fqdn)
            device.ResetDelay()
            device.SetDirectHealthState(HealthState.UNKNOWN)
            device.SetDefective(json.dumps({"enabled": False}))

    def _reset_dishes(self):
        """Reset Dish Devices"""
        # NOTE: maybe just if emulation_configuration.dish: ?
        # NOTE: it does many things

        # if (
        #     SIMULATED_DEVICES_DICT["csp_and_dish"]
        #     or SIMULATED_DEVICES_DICT["all_mocks"]
        # ):
        if (
            emulation_configuration.csp and emulation_configuration.dish
        ) or emulation_configuration.all_emulated():
            for dish_master in self.dish_master_list:
                dish_master.SetDirectDishMode(DishMode.STANDBY_LP)
                dish_master.SetDirectState(DevState.STANDBY)
                dish_master.ResetDelay()
                dish_master.SetDirectHealthState(HealthState.UNKNOWN)

    def _clear_command_call_and_transition_data(self, clear_transition=False):
        """Clears the command call data"""
        # NOTE: this instead may be exactly a duplicate of the central node's
        # _clear_command_call_and_transition_data method

        target_devices = []

        if emulation_configuration.csp:
            target_devices.append(csp_configuration.csp_subarray1_name)

        if emulation_configuration.sdp:
            target_devices.append(sdp_configuration.sdp_subarray1_name)

        if emulation_configuration.dish:
            # NOTE: why just two dishes?
            target_devices.append(dishes_configuration.dish_master1_name)
            target_devices.append(dishes_configuration.dish_master2_name)

        for target_device in target_devices:
            device = DeviceProxy(target_device)
            device.set_timeout_millis(5000)
            device.ClearCommandCallInfo()
            if clear_transition:
                device.ResetTransitions()

        if emulation_configuration.all_production():
            LOGGER.info("Devices deployed are real")

    def tear_down(self):
        """Tear down after each test run"""

        LOGGER.info("Calling Tear down for subarray")
        self._clear_command_call_and_transition_data(clear_transition=True)

        if self.obs_state in ("RESOURCING", "CONFIGURING", "SCANNING"):
            """Invoke Abort and Restart"""
            LOGGER.info("Invoking Abort on Subarray")
            self.abort_subarray()
            self.restart_subarray()
        elif self.obs_state == "ABORTED":
            """Invoke Restart"""
            LOGGER.info("Invoking Restart on Subarray")
            self.restart_subarray()
        else:
            self.force_change_of_obs_state("EMPTY")

        # Move Subarray to OFF state
        self.move_to_off()
        self._reset_dishes()
        self._reset_simulator_devices()
        assert check_subarray_obs_state("EMPTY")

    def clear_all_data(self):
        """Method to clear the observations
        and put the SubarrayNode in EMPTY"""
        if self.obs_state in [
            "IDLE",
            "RESOURCING",
            "READY",
            "CONFIGURING",
            "SCANNING",
        ]:
            self.abort_subarray()
            self.restart_subarray()
        elif self.obs_state == "ABORTED":
            self.restart_subarray()

    def force_change_of_obs_state(
        self,
        dest_state_name: str,
        assign_input_json: str = "",
        configure_input_json: str = "",
        scan_input_json: str = "",
    ) -> None:
        """Force SubarrayNode obsState to provided obsState

        Args:
            dest_state_name (str): Destination obsState
        """
        factory_obj = ObsStateResetterFactory()
        obs_state_resetter = factory_obj.create_obs_state_resetter(
            dest_state_name, self
        )
        if assign_input_json:
            obs_state_resetter.assign_input = assign_input_json
        if configure_input_json:
            obs_state_resetter.configure_input = configure_input_json
        if scan_input_json:
            obs_state_resetter.scan_input = scan_input_json
        obs_state_resetter.reset()
        self._clear_command_call_and_transition_data()

    def simulate_receive_addresses_event(self, sdp_sim, command_input_factory):
        """Sets the receive addresses attribute on SDP Subarray so an event can
        be simulated for Subarray Node to process.
        """
        receive_addresses = prepare_json_args_for_commands(
            "receive_addresses_mid", command_input_factory
        )
        sdp_sim.SetDirectreceiveAddresses(receive_addresses)

        # Setting pointing offsets after encoding the data.
        sdp_qc = DeviceProxy(sdp_queue_connector)
        encoded_data = msgpack.packb(
            POINTING_OFFSETS, default=msgpack_numpy.encode
        )
        sdp_qc.SetDirectPointingOffsets(("msgpack_numpy", encoded_data))

    def execute_five_point_calibration_scan(
        self,
        partial_configure_jsons: list[str],
        scan_jsons: list[str],
        event_recorder,
        command_input_factory,
    ) -> None:
        """Perform a five point calibration scan on Subarray Node using the
        partial configuration jsons and scan jsons provided as inputs.

        Args:
            partial_configure_jsons (list[str]): Partial configuration json
                file names
            scan_jsons (list[str]): Scan json file names
        """
        partial_configure_1 = prepare_json_args_for_commands(
            partial_configure_jsons[0], command_input_factory
        )
        partial_configure_2 = prepare_json_args_for_commands(
            partial_configure_jsons[1], command_input_factory
        )
        partial_configure_3 = prepare_json_args_for_commands(
            partial_configure_jsons[2], command_input_factory
        )
        partial_configure_4 = prepare_json_args_for_commands(
            partial_configure_jsons[3], command_input_factory
        )

        scan_1 = prepare_json_args_for_commands(
            scan_jsons[0], command_input_factory
        )
        scan_2 = prepare_json_args_for_commands(
            scan_jsons[1], command_input_factory
        )
        scan_3 = prepare_json_args_for_commands(
            scan_jsons[2], command_input_factory
        )
        scan_4 = prepare_json_args_for_commands(
            scan_jsons[3], command_input_factory
        )

        # Partial configure 1
        self.execute_transition("Configure", partial_configure_1)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Scan 1
        self.execute_transition("Scan", scan_1)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.SCANNING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Partial configure 2
        self.execute_transition("Configure", partial_configure_2)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Scan 2
        self.execute_transition("Scan", scan_2)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.SCANNING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Partial configure 3
        self.execute_transition("Configure", partial_configure_3)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Scan 3
        self.execute_transition("Scan", scan_3)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.SCANNING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Partial configure 4
        self.execute_transition("Configure", partial_configure_4)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.CONFIGURING,
            lookahead=15,
        )
        assert check_subarray_obs_state(obs_state="READY")

        # Scan 4
        self.execute_transition("Scan", scan_4)
        assert event_recorder.has_change_event_occurred(
            self.subarray_node,
            "obsState",
            ObsState.SCANNING,
            lookahead=15,
        )
        assert check_subarray_obs_state("READY")
