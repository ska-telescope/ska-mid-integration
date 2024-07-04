"""Create a `TelescopeAction` to reset the subarray in a certain obs state."""

from ska_control_model import ObsState

from tests.test_harness2.sut_actions.store_scan_data import StoreScanData
from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_clear_obs_state import (
    SubarrayClearObsState,
)
from tests.test_harness3.telescope_actions.subarray.subarray_execute_transition import (
    SubarrayExecuteTransition,
)
from tests.test_harness3.telescope_actions.subarray.subarray_store_configuration_data import (
    SubarrayStoreConfigurationData,
)
from tests.test_harness3.telescope_actions.subarray.subarray_store_resources import (
    SubarrayStoreResources,
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
    """

    def __init__(
        self,
        telescope: TelescopeWrapper,
        assign_input,
        configure_input,
        scan_input,
    ) -> None:
        self.telescope = telescope
        self.assign_input = assign_input
        self.configure_input = configure_input
        self.scan_input = scan_input

    def create_action_to_reset_subarray_to_empty(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the empty state.

        :return: A `TelescopeAction` to reset the subarray to the empty state.
        """
        return SubarrayClearObsState(self.telescope)

    def create_action_to_reset_subarray_to_resourcing(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the resourcing state.

        :return: A `TelescopeAction` to reset the subarray to the resourcing state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_empty(),
                SubarrayExecuteTransition(
                    self.telescope, "AssignResources", argin=self.assign_input
                ),
            ],
        )

    def create_action_to_reset_subarray_to_idle(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the idle state.

        :return: A `TelescopeAction` to reset the subarray to the idle state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_empty(),
                SubarrayStoreResources(self.telescope, self.assign_input),
            ],
        )

    def create_action_to_reset_subarray_to_aborting(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the aborting state.

        :return: A `TelescopeAction` to reset the subarray to the aborting state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_idle(),
                SubarrayExecuteTransition(self.telescope, "Abort", argin=None),
            ],
        )

    def create_action_to_reset_subarray_to_aborted(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the aborted state.

        :return: A `TelescopeAction` to reset the subarray to the aborted state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_idle(),
                SubarrayAbort(self.telescope),
            ],
        )

    def create_action_to_reset_subarray_to_configuring(
        self,
    ) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the configuring state.

        :return: A `TelescopeAction` to reset the subarray to the configuring state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_idle(),
                # TODO: manage wait_added_for_skb372()
                SubarrayExecuteTransition(
                    self.telescope, "Configure", argin=self.configure_input
                ),
            ],
        )

    def create_action_to_reset_subarray_to_ready(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the ready state.

        :return: A `TelescopeAction` to reset the subarray to the ready state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_idle(),
                # TODO: manage wait_added_for_skb372()
                SubarrayStoreConfigurationData(
                    self.telescope, self.configure_input
                ),
            ],
        )

    def create_action_to_reset_subarray_to_scanning(self) -> TelescopeAction:
        """Create a `TelescopeAction` to reset the subarray to the scanning state.

        :return: A `TelescopeAction` to reset the subarray to the scanning state.
        """
        return TelescopeActionSequence(
            self.telescope,
            [
                self.create_action_to_reset_subarray_to_ready(),
                StoreScanData(self.telescope, self.scan_input),
            ],
        )
