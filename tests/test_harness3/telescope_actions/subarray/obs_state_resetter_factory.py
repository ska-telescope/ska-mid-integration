"""Create a `TelescopeAction` to reset the subarray in a certain obs state."""

import time
from typing import Callable

from ska_control_model import ObsState

from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_assign_resources import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayAssignResources,
)
from tests.test_harness3.telescope_actions.subarray.subarray_clear_obs_state import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayClearObsState,
)
from tests.test_harness3.telescope_actions.subarray.subarray_configure import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayConfigure,
)
from tests.test_harness3.telescope_actions.subarray.subarray_execute_transition import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayExecuteTransition,
)
from tests.test_harness3.telescope_actions.subarray.subarray_scan import (
    SubarrayScan,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.telescope_actions.telescope_action_sequence import (
    TelescopeActionSequence,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.common_utils import JsonFactory


class WaitAddedForSkb372(TelescopeAction):
    """Wait added for SKB-372. TODO: remove this class."""

    def _action(self):
        time.sleep(5)

    def termination_condition(self):
        return []


class SubarrayObsStateResetterFactory:
    """Factory to create `TelescopeAction`s to bring subarray in a obs state.

    This factory is used to create `TelescopeAction`s to bring the subarray
    in a certain obs state. The factory provides methods to create composite
    actions that can move subarray to:

    - Empty state
    - Resourcing state
    - Idle state
    - Aborting state
    - Aborted state
    - Configuring state
    - Ready state
    - Scanning state

    The starting state of the subarray is not considered while creating,
    because all the actions are designed to reset the subarray to
    `EMPTY` state first and then move to the target state.
    """

    def __init__(
        self,
        assign_input: str | None = None,
        configure_input: str | None = None,
        scan_input: str | None = None,
    ) -> None:
        """Initialize with the telescope and (optional) JSON inputs.

        :param assign_input: The input JSON for the `AssignResources` command.
        :param configure_input: The input JSON for the `Configure` command.
        :param scan_input: The input JSON for the `Scan` command.
        """
        self.telescope = TelescopeWrapper()
        json_factory = JsonFactory()

        self.assign_input = (
            assign_input
            or json_factory.create_assign_resources_configuration(
                "assign_resources_mid"
            )
        )
        self.configure_input = (
            configure_input
            or json_factory.create_subarray_configuration("configure_mid")
        )
        self.scan_input = (
            scan_input
            or json_factory.create_subarray_configuration("scan_mid")
        )

    def create_action_to_reset_subarray_to_empty(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `EMPTY`.

        :return: A `TelescopeAction` to reset the subarray to
            the `ObsState.EMPTY` state.
        """
        return SubarrayClearObsState()

    def create_action_to_reset_subarray_to_resourcing(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `RESOURCING`.

        :return: A `TelescopeAction` to reset the subarray to the
            `ObsState.RESOURCING` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_empty(),
                SubarrayExecuteTransition(
                    "AssignResources", argin=self.assign_input
                ),
            ],
        )

    def create_action_to_reset_subarray_to_idle(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the `IDLE`.

        :return: A `TelescopeAction` to reset the subarray to the
            `ObsState.IDLE` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_empty(),
                SubarrayAssignResources(self.assign_input),
            ],
        )

    def create_action_to_reset_subarray_to_aborting(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `ABORTING`.

        :return: A `TelescopeAction` to reset the subarray to
            the `ObsState.ABORTING` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_idle(),
                SubarrayExecuteTransition("Abort", argin=None),
            ],
        )

    def create_action_to_reset_subarray_to_aborted(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `ABORTED`.

        :return: A `TelescopeAction` to reset the subarray to the
            `ObsState.ABORTED` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_idle(),
                SubarrayAbort(),
            ],
        )

    def create_action_to_reset_subarray_to_configuring(
        self,
    ) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `CONFIGURING`.

        :return: A `TelescopeAction` to reset the subarray to
            the `ObsState.CONFIGURING` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_idle(),
                # TODO: manage wait_added_for_skb372()
                WaitAddedForSkb372(),
                SubarrayExecuteTransition(
                    "Configure", argin=self.configure_input
                ),
            ],
        )

    def create_action_to_reset_subarray_to_ready(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `READY`.

        :return: A `TelescopeAction` to reset the subarray to
            the `ObsState.READY` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_idle(),
                # TODO: manage wait_added_for_skb372()
                WaitAddedForSkb372(),
                SubarrayConfigure(self.configure_input),
            ],
        )

    def create_action_to_reset_subarray_to_scanning(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to `SCANNING`.

        :return: A `TelescopeAction` to reset the subarray to
            the `ObsState.SCANNING` state.
        """
        return TelescopeActionSequence(
            [
                self.create_action_to_reset_subarray_to_ready(),
                SubarrayScan(self.scan_input),
            ],
        )

    @property
    def _map_state_to_method(
        self,
    ) -> dict[ObsState, Callable[[], TelescopeAction]]:
        return {
            ObsState.EMPTY: self.create_action_to_reset_subarray_to_empty,
            ObsState.RESOURCING: self.create_action_to_reset_subarray_to_resourcing,  # pylint: disable=line-too-long # noqa: E501
            ObsState.IDLE: self.create_action_to_reset_subarray_to_idle,
            ObsState.ABORTING: self.create_action_to_reset_subarray_to_aborting,  # pylint: disable=line-too-long # noqa: E501
            ObsState.ABORTED: self.create_action_to_reset_subarray_to_aborted,
            ObsState.CONFIGURING: self.create_action_to_reset_subarray_to_configuring,  # pylint: disable=line-too-long # noqa: E501
            ObsState.READY: self.create_action_to_reset_subarray_to_ready,
            ObsState.SCANNING: self.create_action_to_reset_subarray_to_scanning,  # pylint: disable=line-too-long # noqa: E501
        }

    def create_action_to_reset_subarray_to_state(
        self, target_state: ObsState
    ) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the given state.

        :param target_state: The target state to which the subarray should
            be reset.
        :return: A `TelescopeAction` to reset the subarray to the given state.
        """
        return self._map_state_to_method[target_state]()
