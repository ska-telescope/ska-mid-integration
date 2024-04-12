"""
This module is used for testing validations added
for Alarm-Handler configurator API.
"""
import os

import httpx
import pytest

namespace = os.getenv("KUBE_NAMESPACE")
cluster_domain = os.getenv("CLUSTER_DOMAIN", "cluster.local")


def alarm_rule_validation(filename, missing_attribute):
    """Test method to verify validation against alarm rules"""
    with open(
        f"/app/tests/data/alarm_rules/invalid_rules/{filename}", "rb"
    ) as file:
        response = httpx.post(
            f"http://alarm-handler-configurator.{namespace}.svc."
            + f"{cluster_domain}:8004/add-alarms?trl=alarm%2Fhandler%2F01",
            files={"file": (filename, file, "text/plain")},
            data={"trl": "alarm/handler/01"},
        )
        response_data = response.json()
        assert (
            f"Missing {missing_attribute} property in alarm rule"
            in response_data["error"]
        )


@pytest.mark.parametrize(
    "alarm_rule_file, missing_attribute",
    [
        ("missing_tag_attribute.txt", "tag"),
        ("missing_formula_attribute.txt", "formula"),
        ("missing_priority_attribute.txt", "priority"),
        ("missing_group_attribute.txt", "group"),
        ("missing_message_attribute.txt", "message"),
    ],
)
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_validate_attribute_properties(alarm_rule_file, missing_attribute):
    """test case to validate alarm attribute properties for mid"""
    alarm_rule_validation(alarm_rule_file, missing_attribute)
