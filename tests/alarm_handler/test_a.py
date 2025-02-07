"""Test module for TMC-DISH On functionality"""

import json

import pytest


@pytest.mark.batch2
@pytest.mark.SKA_mid
def test_adish_vccc_mock(tmc_mid):
    """
    Test case to verify Dish-VCC validation functionality


    Given a TMC with loaded Dish-VCC map version"""

    cspmln_validation_string = "TMC and CSP Master Dish Vcc Version is Same"
    central_node_dish_vcc_validation_status = {
        "dish": "ALL DISH OK",
        "ska_mid/tm_leaf_node/csp_master": cspmln_validation_string,
    }
    assert (
        json.loads(tmc_mid.DishVccValidationStatus)
        == central_node_dish_vcc_validation_status
    )
    assert tmc_mid.IsDishVccConfigSet
