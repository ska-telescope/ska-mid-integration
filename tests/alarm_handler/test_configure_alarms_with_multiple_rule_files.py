"""
This module is used for testing Alarm-Handler configurator API
with multiple files.
"""
import os

import httpx
import pytest

namespace = os.getenv("KUBE_NAMESPACE")
cluster_domain = os.getenv("CLUSTER_DOMAIN", "cluster.local")


@pytest.mark.xfail(
    reason="Alarm summary key error to be resolved under SAH-1510"
)
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_configure_alarms_with_multiple_files():
    """Test method to configure alarm rules using
    multiple alarm rules files
    """
    for filename in os.listdir("/app/tests/data/alarm_rules/valid_rules/"):
        if filename.endswith(".txt"):
            with open(
                os.path.join(
                    "/app/tests/data/alarm_rules/valid_rules/", filename
                ),
                "r",
            ) as file:
                response = httpx.post(
                    f"http://alarm-handler-configurator.{namespace}.svc."
                    + f"{cluster_domain}:8004/add-alarms?trl="
                    + "alarm%2Fhandler%2F01",
                    files={"file": (filename, file, "text/plain")},
                    data={"trl": "alarm/handler/01"},
                )
    response_data = response.json()
    assert len(response_data["alarm_summary"]["tag"]) == 5
    assert response_data["alarm_summary"]["tag"] == [
        "centralnode_health_degraded",
        "centralnode_health_failed",
        "centralnode_telescopestate_failed",
        "subarraynode_health",
        "subarraynode_obsstate_fault",
    ]
    error_message = "alarm 'centralnode_health_degraded' already exist"
    assert error_message in str(response_data["error"])
    tear_down_alarms(response_data["alarm_summary"]["tag"])


def tear_down_alarms(tags_to_remove):
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
