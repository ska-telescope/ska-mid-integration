"""Invoke configure command on subarray Node."""

import logging

from ska_control_model import ObsState

from tests.resources.test_support.enum import PointingState
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.enums import DishMode
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange

LOGGER = logging.getLogger(__name__)


class SubarrayStoreConfigurationData(TelescopeAction):
    """Invoke configure command on subarray Node."""

    def __init__(self, configure_string: str):
        super().__init__()
        self.configure_string = configure_string

    def _action(self):
        result, message = self.telescope.tmc.subarray_node.Configure(
            self.configure_string
        )
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    def expected_outcome(self):
        # TODO: should add this too?
        # if Resource(device_dict.get("tmc_subarraynode")) == "READY":
        #         invoked_from_ready = True
        # if invoked_from_ready:
        #         the_waiter.set_wait_for_configuring()

        res = [
            ExpectedStateChange(
                self.telescope.tmc.csp_subarray_leaf_node,
                "cspSubarrayObsState",
                ObsState.READY,
            ),
            ExpectedStateChange(
                self.telescope.tmc.sdp_subarray_leaf_node,
                "sdpSubarrayObsState",
                ObsState.READY,
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "obsState", ObsState.READY
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "obsState", ObsState.READY
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node, "obsState", ObsState.READY
            ),
        ]

        for device in self.telescope.dishes.dish_master_list:
            res.extend(
                [
                    ExpectedStateChange(device, "dishMode", DishMode.OPERATE),
                    ExpectedStateChange(
                        device, "pointingState", PointingState.TRACK
                    ),
                ]
            )

        return res
