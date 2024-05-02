"""
This module is used for testing Alarm-Handler configurator API.
"""
import os

import httpx
import pytest

namespace = os.getenv("KUBE_NAMESPACE")
cluster_domain = os.getenv("CLUSTER_DOMAIN", "cluster.local")


def add_alarms_api(filename: str):
    """Test method for add alarms API"""
    with open(
        f"/app/tests/data/alarm_rules/valid_rules/{filename}", "rb"
    ) as file:
        response = httpx.post(
            f"http://alarm-handler-configurator.{namespace}.svc."
            + f"{cluster_domain}:8004/add-alarms?trl=alarm%2Fhandler%2F01",
            files={"file": (filename, file, "text/plain")},
            data={"trl": "alarm/handler/01"},
        )
        response_data = response.json()
        assert len(response_data["alarm_summary"]["tag"]) == 4
        assert response_data["alarm_summary"]["tag"] == [
            "centralnode_health_degraded",
            "centralnode_health_failed",
            "subarraynode_health",
            "subarraynode_obsstate_fault",
        ]


def remove_alarm_api():
    """Test method for remove alarms API"""
    tags_to_remove = [
        "centralnode_health_degraded",
        "centralnode_health_failed",
        "subarraynode_obsstate_fault",
        "subarraynode_health",
    ]
    for tag in tags_to_remove:
        response = httpx.post(
            f"http://alarm-handler-configurator.{namespace}.svc."
            + f"{cluster_domain}:8004/remove-alarm?tag={tag}&"
            + "alarm_handler_trl=alarm%2Fhandler%2F01",
            data={
                "tag": tag,
                "alarm_handler_trl": "alarm/handler/01",
            },
        )
    response_data = response.json()
    assert response_data["alarm_summary"] is None


@pytest.mark.xfail(
    reason="Alarm summary key error to be resolved under SAH-1510"
)
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_configure_alarms():
    """test case to configure alarms for mid"""
    add_alarms_api("alarm_file1.txt")


@pytest.mark.xfail(
    reason="Alarm summary key error to be resolved under SAH-1510"
)
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_remove_alarm():
    """test case to remove alarm for mid"""
    remove_alarm_api()
