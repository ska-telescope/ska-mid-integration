"""Tear down the telescope harness."""

import json
import logging

from ska_control_model import ObsState

from tests.test_harness3.constant import DEFAULT_DISH_VCC_CONFIG
from tests.test_harness3.helpers import check_subarray_obs_state
from tests.test_harness3.telescope_actions.central_node.central_node_load_dish_config import (  # pylint: disable=line-too-long # noqa E501
    CentralNodeLoadDishConfig,
)
from tests.test_harness3.telescope_actions.central_node.central_node_release_resources import (  # pylint: disable=line-too-long # noqa E501
    CentralNodeReleaseResources,
)
from tests.test_harness3.telescope_actions.central_node.move_to_off import (
    MoveToOff,
)
from tests.test_harness3.telescope_actions.subarray.force_change_of_obs_state import (  # pylint: disable=line-too-long # noqa E501
    ForceChangeOfObsState,
)
from tests.test_harness3.telescope_actions.subarray.subarray_move_to_off import (  # pylint: disable=line-too-long # noqa E501
    SubarrayMoveToOff,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.common_utils import JsonFactory

LOGGER = logging.getLogger(__name__)


class TearDownTelescope(TelescopeAction):
    """Tear down the telescope."""

    def _action(self):
        """Perform the action."""
        # Tear down TMC
        Subarray_node_obsstate = self.telescope.tmc.subarray_node.obsState
        LOGGER.info(
            f"Calling tear down for CentralNode for SubarrayNode's \
                {Subarray_node_obsstate} obsstate."
        )

        if self.telescope.tmc.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling Release Resource on centralnode")
            json_factory = JsonFactory()
            release_input = json_factory.create_centralnode_configuration(
                "release_resources_mid"
            )
            CentralNodeReleaseResources(
                self.telescope, release_input
            ).execute()

        ForceChangeOfObsState(self.telescope, ObsState.EMPTY).execute()

        # NOTE: temporarily moved here because of synchronization
        if self.telescope.tmc.telescope_state != "OFF":
            MoveToOff(self.telescope).execute()

        # reset subarray too
        # TODO: maybe TMCCentralNode and TMCSubarrayNode should be
        # two different classes (?).
        SubarrayMoveToOff(self.telescope).execute()

        # if source dish vcc config is empty or not matching with default
        # dish vcc then load default dish vcc config
        # CSP_SIMULATION_ENABLED condition will be removed after testing
        # with real csp
        if (
            not self.telescope.tmc.csp_master_leaf_node.sourceDishVccConfig
            or json.loads(
                self.telescope.tmc.csp_master_leaf_node.sourceDishVccConfig
            )
            != DEFAULT_DISH_VCC_CONFIG
        ):
            CentralNodeLoadDishConfig(
                self.telescope, json.dumps(DEFAULT_DISH_VCC_CONFIG)
            ).execute()

        # Reset other components

        # reset HealthState.UNKNOWN in emulated devices
        # reset command calls and transitions in emulated devices
        self.telescope.sdp.tear_down()
        self.telescope.csp.tear_down()
        self.telescope.dishes.tear_down()

        assert check_subarray_obs_state("EMPTY")

    def expected_outcome(self):
        return []
