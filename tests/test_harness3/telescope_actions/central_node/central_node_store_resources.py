"""Invoke Assign Resource command on CentralNode."""

import json
import logging

from ska_control_model import ObsState

from tests.test_harness3.helpers import generate_eb_pb_ids
from tests.test_harness3.telescope_actions.expected_event import (
    ExpectedStateChange,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class CentralNodeStoreResources(TelescopeAction):
    """Invoke Assign Resource command on CentralNode."""

    # NOTE: this is very similar to SubarrayAssignResources

    def __init__(self, assign_json: str):
        super().__init__()
        self.assign_json = assign_json

    def _action(self):
        # NOTE: should I do this?
        # device = DeviceUtils(
        #     obs_state_device_names=[
        #         device_dict.get("csp_subarray"),
        #         device_dict.get("sdp_subarray"),
        #         device_dict.get("tmc_subarraynode"),
        #     ]
        # )
        # device.check_devices_obsState("EMPTY")
        # set_wait_for_obsstate = kwargs.get("set_wait_for_obsstate", True)

        input_json = json.loads(self.assign_json)
        generate_eb_pb_ids(input_json)
        result, message = self.telescope.tmc.central_node.AssignResources(
            json.dumps(input_json)
        )
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    def termination_condition(self):
        return [
            ExpectedStateChange(
                self.telescope.tmc.csp_subarray_leaf_node,
                "cspSubarrayObsState",
                ObsState.IDLE,
            ),
            ExpectedStateChange(
                self.telescope.tmc.sdp_subarray_leaf_node,
                "sdpSubarrayObsState",
                ObsState.IDLE,
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "obsState", ObsState.IDLE
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "obsState", ObsState.IDLE
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node, "obsState", ObsState.IDLE
            ),
        ]
