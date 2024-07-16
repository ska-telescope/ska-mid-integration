"""Force the change of the ObsState in Subarray."""

import logging

from ska_control_model import ObsState

from tests.test_harness3.common_utils.i_json_factory import IJsonFactory
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
        dest_state_name: ObsState,
        assign_input_json: str | None = None,
        configure_input_json: str | None = None,
        scan_input_json: str | None = None,
        json_factory: IJsonFactory | None = None,
    ):
        """Initialize the action with the target state and the JSON inputs.

        To init correctly this class you should provide:

        - all the JSON inputs for the `AssignResources`, `Configure` and `Scan`
            commands, or
        - a JSON factory to create the default JSON inputs for these commands.

        You can also provide just some inputs and the factory will create the
        default JSON inputs for the rest. If not all inputs are provided
        and the factory is not provided either, the creation will raise
        a ValueError.

        :param dest_state_name: The target state to reach.
        :param assign_input_json: The input JSON for the
            `AssignResources` command.
        :param configure_input_json: The input JSON for
            the `Configure` command.
        :param scan_input_json: The input JSON for the `Scan` command.
        :param json_factory: The factory to create the default JSON inputs.
        """
        super().__init__()

        self.dest_state_name = dest_state_name
        self.assign_input_json = assign_input_json
        self.configure_input_json = configure_input_json
        self.scan_input_json = scan_input_json
        self.json_factory = json_factory

    def _action(self):
        LOGGER.info("Forcing the change of ObsState in Subarray")

        obs_state_resetter_action = SubarrayObsStateResetterFactory(
            self.assign_input_json,
            self.configure_input_json,
            self.scan_input_json,
            self.json_factory,
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
