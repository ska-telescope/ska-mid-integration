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
    """Force the change of the ObsState in Subarray to a target state.

    This action is used to force the change of the ObsState in TMC Subarray,
    regardless of the current state of the Subarray.
    The action will move the state machine to the target state, by executing
    the necessary steps to reach it (e.g. assign, configure, scan) in a
    correct and consistent way.

    This action has no termination condition, but you can custumize:

    - the wait timeout of each of the steps, by calling the method
        ``set_termination_condition_timeout(timeout)``.
    - the termination condition policy of the last step, by calling the method
        ``set_termination_condition_policy(True)`` (to ensure all
        steps wait for the termination condition) or
        ``set_termination_condition_policy(False)`` (to make the last step
        not wait for the termination condition).

    By default each step will keep the default wait termination condition
    and each step will wait for its termination condition.
    """

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

        obs_state_resetter_action.set_termination_condition_timeout(
            self.termination_condition_timeout
        )
        obs_state_resetter_action.set_termination_condition_policy(
            self.wait_termination_condition
        )

        obs_state_resetter_action.execute()

        self.telescope.clear_command_call()

    def termination_condition(self):
        """No expected outcome for this action."""
        return []
