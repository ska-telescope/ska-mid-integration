"""Perform a five point calibration scan on Subarray Node using the
partial configuration jsons and scan jsons provided as inputs.
"""

from assertpy import assert_that
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer

from tests.test_harness3.helpers import (
    check_subarray_obs_state,
    prepare_json_args_for_commands,
)
from tests.test_harness3.telescope_actions.subarray.subarray_execute_transition import (  # pylint: disable=line-too-long # noqa E501
    SubarrayExecuteTransition,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


class SubarrayFivePointCalibrationScan(TelescopeAction):
    """Perform a five point calibration scan on Subarray Node using the
    partial configuration jsons and scan jsons provided as inputs.
    """

    TRACER_TIMEOUT = 50

    def __init__(
        self,
        partial_configure_jsons: list[str],
        scan_jsons: list[str],
        command_input_factory,
    ):
        super().__init__()
        self.partial_configure_jsons = partial_configure_jsons
        self.scan_configuration = scan_jsons
        self.command_input_factory = command_input_factory

    def _action(self):

        partial_configure = []
        scan = []

        for i in range(4):
            partial_configure.append(
                prepare_json_args_for_commands(
                    self.partial_configure_jsons[i], self.command_input_factory
                )
            )
            scan.append(
                prepare_json_args_for_commands(
                    self.scan_configuration[i], self.command_input_factory
                )
            )

        event_tracer = TangoEventTracer()
        event_tracer.subscribe_event(
            self.telescope.tmc.subarray_node,
            "obsState",
        )

        for i in range(4):

            # Partial configure
            SubarrayExecuteTransition(
                "Configure", partial_configure[i]
            ).execute()
            assert_that(event_tracer).described_as(
                f"In scan {i+1} Subarray obsState should reach CONFIGURING"
            ).within_timeout(self.TRACER_TIMEOUT).has_change_event_occurred(
                self.telescope.tmc.subarray_node,
                "obsState",
                ObsState.CONFIGURING,
            )
            assert check_subarray_obs_state(obs_state="READY")

            # Scan
            SubarrayExecuteTransition("Scan", scan[i]).execute()
            assert_that(event_tracer).described_as(
                f"In scan {i+1} Subarray obsState should reach SCANNING"
            ).within_timeout(self.TRACER_TIMEOUT).has_change_event_occurred(
                self.telescope.tmc.subarray_node,
                "obsState",
                ObsState.SCANNING,
            )
            assert check_subarray_obs_state(obs_state="READY")

            event_tracer.clear_events()

    def termination_condition(self):
        return []
