"""Tool to move the subarray observation state to a specific state."""

import abc

from tests.test_harness3.telescope_actions.subarray.store_scan_data import (
    SubarrayStoreScanData,
)
from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_clear_obs_state import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayClearObsState,
)
from tests.test_harness3.telescope_actions.subarray.subarray_execute_transition import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayExecuteTransition,
)
from tests.test_harness3.telescope_actions.subarray.subarray_store_configuration_data import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayStoreConfigurationData,
)
from tests.test_harness3.telescope_actions.subarray.subarray_store_resources import (  # pylint: disable=line-too-long # noqa: E501
    SubarrayStoreResources,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.common_utils import (
    JsonFactory,
    wait_added_for_skb372,
)


class ObsStateResetter(abc.ABC):
    """Tool to move the subarray observation state to a specific state."""

    def __init__(self, name: str, telescope: TelescopeWrapper):
        self.name = name
        self.telescope = telescope

        self.json_factory = JsonFactory()
        self.assign_input = (
            self.json_factory.create_assign_resources_configuration(
                "assign_resources_mid"
            )
        )
        self.configure_input = self.json_factory.create_subarray_configuration(
            "configure_mid"
        )
        self.scan_input = self.json_factory.create_subarray_configuration(
            "scan_mid"
        )

    @abc.abstractmethod
    def reset(self):
        """Move the subarray observation state to a specific state."""
        pass


class ReadyObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "READY" state
    and reset the relevant values (resources and configurations)
    """

    state_name = "READY"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()
        wait_added_for_skb372()
        SubarrayStoreConfigurationData(
            self.telescope, self.configure_input
        ).execute()


class IdleObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "IDLE" state
    and reset the relevant values (resources)
    """

    state_name = "IDLE"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()


class EmptyObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "EMPTY" state
    """

    state_name = "EMPTY"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()


class ResourcingObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "RESOURCING" state
    """

    state_name = "RESOURCING"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayExecuteTransition(
            self.telescope, "AssignResources", argin=self.assign_input
        ).execute()


class ConfiguringObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "CONFIGURING" state
    """

    state_name = "CONFIGURING"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()
        wait_added_for_skb372()
        SubarrayExecuteTransition(
            self.telescope, "Configure", argin=self.configure_input
        ).execute()


class AbortingObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "ABORTING" state
    """

    state_name = "ABORTING"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()
        SubarrayExecuteTransition(
            self.telescope, "Abort", argin=None
        ).execute()


class AbortedObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "ABORTED" state
    """

    state_name = "ABORTED"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()
        SubarrayAbort(self.telescope).execute()


class ScanningObsStateResetter(ObsStateResetter):
    """
    Put self.device into the "ABORTED" state
    """

    state_name = "SCANNING"

    def reset(self):
        SubarrayClearObsState(self.telescope).execute()
        SubarrayStoreResources(self.telescope, self.assign_input).execute()
        wait_added_for_skb372()
        SubarrayStoreConfigurationData(
            self.telescope, self.configure_input
        ).execute()
        SubarrayStoreScanData(self.telescope, self.scan_input).execute()


class ObsStateResetterFactory:
    """Factory class to create ObsStateResetter instances."""

    table = {
        "EMPTY": EmptyObsStateResetter,
        "RESOURCING": ResourcingObsStateResetter,
        "IDLE": IdleObsStateResetter,
        "CONFIGURING": ConfiguringObsStateResetter,
        "READY": ReadyObsStateResetter,
        "ABORTING": AbortingObsStateResetter,
        "ABORTED": AbortedObsStateResetter,
        "SCANNING": ScanningObsStateResetter,
    }

    def create_obs_state_resetter(
        self, state_name: str, telescope: TelescopeWrapper
    ):
        """Create an ObsStateResetter instance."""
        obs_state_resetter = self.table[state_name](state_name, telescope)
        return obs_state_resetter
