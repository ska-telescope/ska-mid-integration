"""Force the change of the ObsState in Subarray."""

import logging

from tests.test_harness3.telescope_actions.subarray.obs_state_resetter_factory import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayObsStateResetterFactory,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class ForceChangeOfObsState(TelescopeAction):
    """Force the change of the ObsState in Subarray to a target state."""

    def __init__(
        self,
        telescope,
        dest_state_name: str,
        assign_input_json: str | None = None,
        configure_input_json: str | None = None,
        scan_input_json: str | None = None,
    ):
        """Initialize the action with the target state."""
        super().__init__(telescope)

        self.dest_state_name = dest_state_name
        self.assign_input_json = assign_input_json
        self.configure_input_json = configure_input_json
        self.scan_input_json = scan_input_json

    def _action(self):
        LOGGER.info("Forcing the change of ObsState in Subarray")
        # factory_obj = ObsStateResetterFactory()
        # obs_state_resetter = factory_obj.create_obs_state_resetter(
        #     self.dest_state_name, self.telescope
        # )
        # if self.assign_input_json:
        #     obs_state_resetter.assign_input = self.assign_input_json
        # if self.configure_input_json:
        #     obs_state_resetter.configure_input = self.configure_input_json
        # if self.scan_input_json:
        #     obs_state_resetter.scan_input = self.scan_input_json
        # obs_state_resetter.reset()

        obs_state_resetter_action = SubarrayObsStateResetterFactory(
            self.telescope,
            self.assign_input_json,
            self.configure_input_json,
            self.scan_input_json,
        ).create_action_to_reset_subarray_to_state(self.dest_state_name)

        obs_state_resetter_action.execute()

        # self.subarray_node_facade._clear_command_call_and_transition_data()
        self.telescope.clear_command_call()

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
