"""TMC Mid executes multiple scans with different
configurations, intermittently ending configurations"""

import logging

import pytest
from pytest_bdd import scenario
from ska_ser_logging import configure_logging

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="SKB-332 has been raised for this issue")
@pytest.mark.xfail(reason="Need to raise bug on SDP")
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-39939_long_sequence_with_end.feature",
    "TMC Mid executes multiple scans with different configurations,"
    " intermittently ending configurations",
)
def test_tmc_sdp_long_sequences():
    """
    Test case to verify TMC Mid executes multiple scans with different
    configurations, intermittently ending configurations
    """
