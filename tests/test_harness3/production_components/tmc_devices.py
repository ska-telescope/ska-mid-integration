"""Production wrapper for TMC devices."""

import json
import logging

from ska_control_model import ObsState
from ska_ser_logging import configure_logging

from tests.test_harness3.constant import DEFAULT_DISH_VCC_CONFIG
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
from tests.test_harness3.telescope_config.components_config import (
    TMCConfiguration,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.telescope_structure.tmc_devices import TMCDevices
from tests.test_harness3.utils.common_utils import JsonFactory

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class ProductionTMCDevices(TMCDevices):
    """Production wrapper for TMC devices."""

    def __init__(
        self,
        tmc_configuration: TMCConfiguration,
    ):
        super().__init__(tmc_configuration)

        # NOTE: even if it not technically circular, this dependency
        # is a bit weird. Maybe it could be refactored. See init package
        # for more details.
        self._telescope: TelescopeWrapper = None

    def set_telescope(self, telescope: TelescopeWrapper) -> None:
        """Set the telescope wrapper."""
        self._telescope = telescope

    def tear_down(self) -> None:
        """Tear down the TMC devices."""
        Subarray_node_obsstate = self.subarray_node.obsState
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
            CentralNodeReleaseResources(
                self._telescope, release_input
            ).execute()

        ForceChangeOfObsState(self._telescope, ObsState.EMPTY).execute()

        # NOTE: temporarily moved here because of synchronization
        if self.telescope_state != "OFF":
            MoveToOff(self._telescope).execute()

        # reset subarray too
        # TODO: maybe TMCCentralNode and TMCSubarrayNode should be
        # two different classes (?).
        SubarrayMoveToOff(self._telescope).execute()

        # if source dish vcc config is empty or not matching with default
        # dish vcc then load default dish vcc config
        # CSP_SIMULATION_ENABLED condition will be removed after testing
        # with real csp
        if (
            not self.csp_master_leaf_node.sourceDishVccConfig
            or json.loads(self.csp_master_leaf_node.sourceDishVccConfig)
            != DEFAULT_DISH_VCC_CONFIG
        ):
            CentralNodeLoadDishConfig(
                self._telescope, json.dumps(DEFAULT_DISH_VCC_CONFIG)
            ).execute()
