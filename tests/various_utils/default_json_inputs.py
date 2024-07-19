"""A collection of default JSON inputs for various devices."""

from tests.test_harness3.telescope_inputs.dict_json_input import DictJSONInput
from tests.various_utils.file_json_input import FileJSONInput

CONFIGURE_SUBARRAY_INPUT = FileJSONInput("subarray", "configure_mid")
SCAN_SUBARRAY_INPUT = FileJSONInput("subarray", "scan_mid")
ASSIGN_SUBARRAY_INPUT = FileJSONInput("subarray", "assign_resources_mid")

ASSING_CENTRAL_NODE_INPUT = FileJSONInput(
    "centralnode", "assign_resources_mid"
)
RELEASE_CENTRAL_NODE_INPUT = FileJSONInput(
    "centralnode", "release_resources_mid"
)

DEFAULT_VCC_CONFIG_INPUT = DictJSONInput(
    {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "tm_data_sources": [
            "car://gitlab.com/ska-telescope/ska-telmodel-data?"
            + "ska-sdp-tmlite-repository-1.0.0#tmdata"
        ],
        "tm_data_filepath": (
            "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
        ),
    }
)
