import pytest
import tango
from ska_tango_base.control_model import HealthState

from tests.conftest import LOGGER
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
    get_master_device_simulators,
)


class TestTelescopeHealthState(object):
    """This class implement test cases to verify telescopeHealthState
    of CentralNode
    This tests implement rows of decision table for telescopeHealthState,
    following excel sheet
    https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=825874621
    """

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state, \
        dish_master3_health_state, dish_master4_health_state",
        [
            # decision table row 5 to row 9
            (
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.batch2
    @pytest.mark.SKA_mid
    def test_telescope_health_state_failed(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
        dish_master3_health_state,
        dish_master4_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
        dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.FAILED,
        )

    @pytest.mark.batch21
    @pytest.mark.SKA_mid
    def test_telescope_health_state_ok(
        self,
        central_node_mid,
        subarray_node,
        event_recorder,
        simulator_factory,
    ):
        # decision table row 3
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ) = get_master_device_simulators(simulator_factory)

        csp_master_sim.SetDirectHealthState(HealthState.OK)
        sdp_master_sim.SetDirectHealthState(HealthState.OK)
        dish_master_sim_1.SetDirectHealthState(HealthState.OK)
        dish_master_sim_2.SetDirectHealthState(HealthState.OK)
        dish_master_sim_3.SetDirectHealthState(HealthState.OK)
        dish_master_sim_4.SetDirectHealthState(HealthState.OK)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        event_recorder.subscribe_event(csp_master_sim, "healthState")
        event_recorder.subscribe_event(sdp_master_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(dish_master_sim_3, "healthState")
        event_recorder.subscribe_event(dish_master_sim_4, "healthState")

        assert event_recorder.has_change_event_occurred(
            csp_master_sim, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"
        assert event_recorder.has_change_event_occurred(
            sdp_master_sim, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"
        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"
        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"
        assert event_recorder.has_change_event_occurred(
            dish_master_sim_3, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"
        assert event_recorder.has_change_event_occurred(
            dish_master_sim_4, "healthState", HealthState.OK
        ), "Expected HealthState to be OK"

        devices = "csp subarray,sdp subarray,csp subarray2,sdp subarray2"
        devices_list = devices.split(",")
        health_state = "OK,OK,OK,OK"
        health_state_list = health_state.split(",")

        sim_devices_list = get_device_simulator_with_given_name(
            simulator_factory, devices_list
        )
        LOGGER.info("Sim Devices List: %s", sim_devices_list)
        for sim_device, sim_health_state_val in list(
            zip(sim_devices_list, health_state_list)
        ):
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])

        LOGGER.info(
            "Dish Master 1 HealthState: %s", dish_master_sim_1.healthState
        )
        LOGGER.info(
            "Dish Master 2 HealthState: %s", dish_master_sim_2.healthState
        )
        LOGGER.info(
            "Dish Master 3 HealthState: %s", dish_master_sim_3.healthState
        )
        LOGGER.info(
            "Dish Master 4 HealthState: %s", dish_master_sim_4.healthState
        )
        LOGGER.info("CSP Master HealthState: %s", csp_master_sim.healthState)
        LOGGER.info("SDP Master HealthState: %s", sdp_master_sim.healthState)
        LOGGER.info(
            "CSP Subarray HealthState: %s", sim_devices_list[0].healthState
        )
        LOGGER.info(
            "SDP Subarray HealthState: %s", sim_devices_list[1].healthState
        )
        LOGGER.info(
            "CSP Subarray2 HealthState: %s", sim_devices_list[2].healthState
        )
        LOGGER.info(
            "SDP Subarray2 HealthState: %s", sim_devices_list[3].healthState
        )

        LOGGER.info("Csp Master AdminMode: %s", csp_master_sim.adminMode)
        LOGGER.info("Sdp Master AdminMode: %s", sdp_master_sim.adminMode)
        LOGGER.info(
            "CSP Subarray AdminMode: %s", sim_devices_list[0].adminMode
        )
        LOGGER.info(
            "SDP Subarray AdminMode: %s", sim_devices_list[1].adminMode
        )
        LOGGER.info(
            "CSP Subarray2 AdminMode: %s", sim_devices_list[2].adminMode
        )
        LOGGER.info(
            "SDP Subarray2 AdminMode: %s", sim_devices_list[3].adminMode
        )
        LOGGER.info(
            "Subarray Node1 HealthState: %s",
            subarray_node.subarray_node.healthState,
        )
        subarray_node2 = tango.DeviceProxy("mid-tmc/subarray/02")
        LOGGER.info(
            "SubarrayNode 2 HealthState: %s", subarray_node2.healthState
        )
        LOGGER.info(
            "Central Node Telescope HealthState: %s",
            central_node_mid.central_node.telescopeHealthState,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.OK,
            10,
        ), "Expected Telescope HealthState to be OK"

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state, \
        dish_master3_health_state, dish_master4_health_state",
        [
            # decision table row 11 to row 15
            (
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.batch2
    @pytest.mark.SKA_mid
    def test_telescope_health_state_degraded(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
        dish_master3_health_state,
        dish_master4_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
        dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.DEGRADED,
        ), "Expected Telescope HealthState to be DEGRADED"

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state, \
        dish_master3_health_state, dish_master4_health_state",
        [
            # decision table row 17 to row 21
            (
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.batch2
    @pytest.mark.SKA_mid
    def test_telescope_health_state_unknown(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
        dish_master3_health_state,
        dish_master4_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
        dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.UNKNOWN,
        ), "Expected Telescope HealthState to be UNKNOWN"
