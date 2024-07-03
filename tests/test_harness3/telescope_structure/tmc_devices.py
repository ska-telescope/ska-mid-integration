"""A wrapper for the TMC component."""

import logging

from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.test_harness3.telescope_config.components_config import (
    TMCConfiguration,
)
from tests.test_harness3.utils.common_utils import JsonFactory

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TMCDevices:
    """A wrapper for the TMC component."""

    def __init__(self, tmc_configuration: TMCConfiguration):
        """Initialise the TMC wrapper.

        Args:
            tmc_configuration: The TMC configuration.
        """
        self.central_node = DeviceProxy(tmc_configuration.centralnode_name)
        self.central_node.set_timeout_millis(5000)

        self.subarray_node = DeviceProxy(
            tmc_configuration.tmc_subarraynode1_name
        )
        self.subarray_node.set_timeout_millis(5000)

        self.csp_master_leaf_node = DeviceProxy(
            tmc_configuration.tmc_csp_master_leaf_node_name
        )
        self.sdp_master_leaf_node = DeviceProxy(
            tmc_configuration.tmc_sdp_master_leaf_node_name
        )

        # NOTE: not so much used EXTERNALLY, internally just on this
        # constructor. So what is the sense of this list?
        self.dish_leaf_node_list = [  # Those instead are inside TMC
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node1_name),
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node2_name),
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node3_name),
            DeviceProxy(tmc_configuration.tmc_dish_leaf_node4_name),
        ]

        for dish_leaf_node in self.dish_leaf_node_list:
            dish_leaf_node.set_timeout_millis(5000)

        # Create Dish1 leaf node admin device proxy
        self.dish1_leaf_admin_dev_name = self.dish_leaf_node_list[0].adm_name()
        self.dish1_leaf_admin_dev_proxy = DeviceProxy(
            self.dish1_leaf_admin_dev_name
        )

        self._state = DevState.OFF

        # NOTE: `state` is never used

        # initialize in advance the release resources input json
        json_factory = JsonFactory()
        self.release_input = json_factory.create_centralnode_configuration(
            "release_resources_mid"
        )

    # -----------------------------------------------------------
    # CentralNode properties

    @property
    def state(self) -> DevState:
        """TMC CentralNode operational state"""
        self._state = Resource(self.central_node).get("State")
        return self._state

    @state.setter
    def state(self, value: DevState):
        """Sets value for TMC CentralNode operational state

        Args:
            value (DevState): operational state value
        """
        # NOTE: what is the sense of this setter? If I will ever
        # access it through the getter it will always use an updated
        # value from the device. So, this setter is useless (unless
        # you directly access `self._state`, but 1) it's never done and
        # 2) it is an anti-pattern...). It may be something that ideally
        # is used to change central_node state (?)
        self._state = value

    @property
    def IsDishVccConfigSet(self):
        """Return DishVccConfigSet flag"""
        return self.central_node.isDishVccConfigSet

    @property
    def DishVccValidationStatus(self):
        """Current dish vcc validation status of central node"""
        return self.central_node.DishVccValidationStatus

    @property
    def telescope_health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._telescope_health_state = Resource(self.central_node).get(
            "telescopeHealthState"
        )
        return self._telescope_health_state

    @telescope_health_state.setter
    def telescope_health_state(self, value: HealthState) -> None:
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        # NOTE: same as for `state`
        self._telescope_health_state = value

    # NOTE: same as for `state`
    @property
    def telescope_state(self) -> DevState:
        """Telescope state representing overall state of telescope"""

        self._telescope_state = Resource(self.central_node).get(
            "telescopeState"
        )
        return self._telescope_state

    @telescope_state.setter
    def telescope_state(self, value: DevState) -> None:
        """Telescope state representing overall state of telescope

        Args:
            value (DevState): telescope state value
        """
        # NOTE: this setter is never used + same as for `state`
        self._telescope_state = value

    # -----------------------------------------------------------
    # Subarray node properties

    @property
    def subarray_state(self) -> DevState:
        """TMC SubarrayNode operational state"""
        self._state = Resource(self.subarray_node).get("State")
        return self._state

    @subarray_state.setter
    def subarray_state(self, value):
        """Sets value for TMC subarrayNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    # -----------------------------------------------------------
    # Subarray state actions

    def set_subarray_id(self, subarray_id: int):
        """Set subarray ID"""

        self.subarray_node = DeviceProxy(
            f"ska_mid/tm_subarray_node/{subarray_id}"
        )

        # NOTE: why zfill(2) after the first DeviceProxy creation?
        subarray_id = str(subarray_id).zfill(2)

        self.csp_subarray_leaf_node = DeviceProxy(
            f"ska_mid/tm_leaf_node/csp_subarray{subarray_id}"
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            f"ska_mid/tm_leaf_node/sdp_subarray{subarray_id}"
        )

    # -----------------------------------------------------------
    # Teardown actions

    # def tear_down(self):
    #     """Teardown the TMC"""
    #     self._reset_subarray_obs_state()
    #     self._reset_telescope_state()

    # def _reset_subarray_obs_state(self):
    #     """Reset subarray obs state"""
    #     Subarray_node_obsstate = self.subarray_node.obsState
    #     LOGGER.info(
    #         f"Calling tear down for CentralNode for SubarrayNode's \
    #             {Subarray_node_obsstate} obsstate."
    #     )

    #     if self.subarray_node.obsState == ObsState.IDLE:
    #         LOGGER.info("Calling Release Resource on centralnode")
    #         self.invoke_release_resources(self.release_input)
    #     elif self.subarray_node.obsState in [
    #         ObsState.RESOURCING,
    #         ObsState.SCANNING,
    #         ObsState.CONFIGURING,
    #         ObsState.READY,
    #         ObsState.IDLE,
    #     ]:
    #         LOGGER.info("Calling Abort and Restart on SubarrayNode")
    #         self.subarray_abort()
    #         self.subarray_restart()
    #     elif self.subarray_node.obsState == ObsState.ABORTED:
    #         self.subarray_restart()

    # def _reset_telescope_state(self) -> None:
    #     """Reset telescope state"""
    #     if self.telescope_state != "OFF":
    #         self.move_central_node_to_off()
