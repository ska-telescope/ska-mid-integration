import os
from typing import Any, Literal, TypedDict

from ska_ser_skuid.client import SkuidClient
from tango import Database, DeviceProxy


class Env(TypedDict):
    namespace: str
    telescope: str | None
    database_name: str
    job_id: str | None
    SDP_CONFIG_HOST: str
    ingress_name: str


env = Env(
    namespace="",
    telescope="",
    database_name="",
    job_id="",
    SDP_CONFIG_HOST="",
    ingress_name="",
)


# ========= FUNCTIONS USED IN NOTEBOOKS ================#
def set_cluster(
    job_id: str | None = None,
    namespace: str = "staging",
    telescope: str | None = "mid",
    database_name: str = "databaseds-tango-base",
    facility: Literal["stfc", "itf"] = "stfc",
    db_port: int | None = 10000,
    polling: bool = False,
    helm_release: str | None = None,
) -> int:
    """
    Set the cluster environment variables
    :param job_id: job id
    :param namespace: namespace
    :param telescope: telescope
    :param database_name: database name
    :param facility: facility
    :param db_port: database port
    :param polling: use polling
    :return: result of smoke test
    """
    facility_name = {
        "stfc": "techops.internal.skao.int",
        "itf": "miditf.internal.skao.int",
    }.get(facility)
    if telescope is None:
        telescope_annotation = ""
    else:
        telescope_annotation = f"-{telescope}"
    os.environ["TANGO_HOST"] = (
        f"{database_name}.{namespace}{telescope_annotation}.svc.{facility_name}:{db_port}"
    )
    if helm_release:
        os.environ["SKUID_URL"] = (
            f"ska-ser-skuid-{helm_release}-svc.{namespace}{telescope_annotation}.svc.{facility_name}:9870"
        )
    if polling:
        os.environ["USE_POLLING"] = "True"
    env["database_name"] = database_name
    env["namespace"] = namespace
    env["telescope"] = telescope
    env["job_id"] = job_id
    env["SDP_CONFIG_HOST"] = f"ska-sdp-etcd-client.namespace-{namespace}"
    assert facility_name
    ingress_name = {
        "stfc": "k8s.stfc.skao.int",
        "itf": "k8s.miditf.internal.skao.int",
    }.get(facility)
    assert ingress_name
    env["ingress_name"] = ingress_name
    return smoke_test_cluster()


def smoke_test_cluster() -> int:
    """Smoke test cluster by pinging Database"""
    result = DeviceProxy("sys/database/2").ping()
    if env["job_id"]:
        get_skuid_cli().get_local_transaction_id()
    return result


def set_oda_url(
    namespace: str = "staging-ska-db-oda",
    facility: Literal["stfc", "itf"] = "stfc",
):
    """
    Set ODA_URI environment variable used by the OSO scripting library
    (ska-oso-scripting) to save Execution Blocks into.

    If namespace is not set, the URI will default to the ODA staging deployment.
    """
    facility_name = {
        "stfc": "techops.internal.skao.int",
        "itf": "miditf.internal.skao.int",
    }.get(facility)
    os.environ["ODA_URL"] = (
        f"http://ingress-nginx-controller-lb-stfc-techops-production-cicd.ingress-nginx.svc.{facility_name}/{namespace}/oda/api/v5"
    )


# ======== UNUSED FUNCTIONS ================#
def disable_qa():
    """
    Disable QA
    :return: None
    """
    os.environ["DISABLE_QA"] = "True"


def get_sdp_config_host() -> str:
    """
    Get sdp config host

    :return: sdp config host
    """
    return env["SDP_CONFIG_HOST"]


# ska-ser-skuid-test-mid-3236408314-svc.staging-mid.svc.cluster.local
def get_skuid_cli():
    """
    Get skuid cli

    :return: skuid cli
    """
    assert env[
        "job_id"
    ], "job_id can't be empty, did you call `set_cluster()`?"
    if env["namespace"].find("staging") != -1:
        name = f'ska-ser-skuid-staging-{env["telescope"]}-{env["job_id"]}-svc'
    else:
        name = f'ska-ser-skuid-test-{env["telescope"]}-{env["job_id"]}-svc'
    cluster = "svc.techops.internal.skao.int:9870"
    skuid_url = f'{name}.{env["namespace"]}.{cluster}'
    return SkuidClient(skuid_url)


def get_namespace() -> str:
    """
    Get namespace
    :return: namespace
    """
    return env["namespace"]
