"""Test TMC Mid executes configure-scan sequence of commands successfully"""

import logging

import pytest
from pytest_bdd import scenario
from ska_ser_logging import configure_logging

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="STS-855-SDP side Issue")
# SDP Side Issue: Docker images in Harbor overwritten by new releases
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-35244_long_sequence_configure_scan.feature",
    "TMC Mid executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Mid executes configure-scan sequence of commands successfully
    """
