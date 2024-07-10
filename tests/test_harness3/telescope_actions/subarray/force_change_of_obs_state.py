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
        dest_state_name: str,
        assign_input_json: str | None = None,
        configure_input_json: str | None = None,
        scan_input_json: str | None = None,
    ):
        """Initialize the action with the target state."""
        super().__init__()

        self.dest_state_name = dest_state_name
        self.assign_input_json = assign_input_json
        self.configure_input_json = configure_input_json
        self.scan_input_json = scan_input_json

    def _action(self):
        LOGGER.info("Forcing the change of ObsState in Subarray")

        obs_state_resetter_action = SubarrayObsStateResetterFactory(
            self.assign_input_json,
            self.configure_input_json,
            self.scan_input_json,
        ).create_action_to_reset_subarray_to_state(self.dest_state_name)

        obs_state_resetter_action.execute()

        self.telescope.clear_command_call()

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
