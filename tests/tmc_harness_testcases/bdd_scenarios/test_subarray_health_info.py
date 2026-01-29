import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import HealthState, ObsState

from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.enums import CapabilityStates


@pytest.mark.batch2test
@pytest.mark.SKA_mid
@scenario(
    "../features/subarray_healthinfo.feature",
    "Dish health failure is reflected in Subarray HealthInfo",
)
def test_subarray_healthinfo():
    """Dish failure propagates to Subarray HealthInfo"""


@pytest.mark.SKA_mid
@scenario(
    "../features/subarray_healthinfo.feature",
    "Dish health recovers and Subarray HealthInfo is updated",
)
def test_subarray_healthinfo_recovery():
    """Dish recovery propagates to Subarray HealthInfo"""


# -------------------------
# GIVEN STEPS
# -------------------------


@given("the subarray is in ON state")
def given_subarray_on(subarray_node: SubarrayNodeWrapper):
    subarray_node.move_to_on()
    subarray_node.force_change_of_obs_state("EMPTY")


@given("dishes are assigned to the subarray")
def given_dishes_assigned(
    subarray_node,
    event_recorder,
    command_input_factory,
):
    input_json = prepare_json_args_for_commands(
        "assign_resources_mid", command_input_factory
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node,
        "obsState",
    )

    subarray_node.execute_transition("AssignResources", argin=input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@given(parsers.parse('dish "{dish_name}" is in FAILED state'))
def given_dish_failed(dish_master):
    capability_json = json.dumps({"B2": CapabilityStates.UNAVAILABLE})
    dish_master.SetDirectCapabilityState(capability_json)


# -------------------------
# WHEN STEPS
# -------------------------


@when(parsers.parse('dish "{dish_name}" capability state becomes UNAVAILABLE'))
def when_dish_becomes_unavailable(dish_master):
    capability_json = json.dumps({"B2": CapabilityStates.UNAVAILABLE})
    dish_master.SetDirectCapabilityState(capability_json)


@when(parsers.parse('dish "{dish_name}" capability state becomes AVAILABLE'))
def when_dish_becomes_available(dish_master):
    capability_json = json.dumps({"B2": CapabilityStates.OPERATE_FULL})
    dish_master.SetDirectCapabilityState(capability_json)


# -------------------------
# THEN STEPS
# -------------------------


@then(
    parsers.parse(
        'subarray health info should show dish "{dish_name}" '
        "as {expected_state}"
    )
)
def then_dish_healthinfo_reflected(
    subarray_node,
    event_recorder,
    dish_name,
    expected_state,
):
    event_recorder.subscribe_event(
        subarray_node.subarray_node,
        "healthReport",
    )

    def _healthinfo_match(event):
        report = event.attr_value
        return (
            dish_name in report
            and report[dish_name]["healthState"] == HealthState[expected_state]
        )

    assert event_recorder.has_event_occurred(
        subarray_node.subarray_node,
        "healthReport",
        _healthinfo_match,
    ), (
        f"Dish {dish_name} not reflected as "
        f"{expected_state} in Subarray HealthInfo"
    )


@then(
    parsers.parse('the health info reason should contain "{expected_reason}"')
)
def then_healthinfo_reason_contains(
    subarray_node,
    event_recorder,
    expected_reason,
):
    def _reason_check(event):
        report = event.attr_value
        for device in report.values():
            if device[
                "healthState"
            ] == HealthState.FAILED and expected_reason in device.get(
                "reason", ""
            ):
                return True
        return False

    assert event_recorder.has_event_occurred(
        subarray_node.subarray_node,
        "healthReport",
        _reason_check,
    ), "Expected failure reason not found in Subarray HealthInfo"
