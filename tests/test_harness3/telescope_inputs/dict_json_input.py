"""A JSON input for the subarray, built around a dictionary."""

import json

from tests.test_harness3.telescope_inputs.json_input import JSONInput


class DictJSONInput(JSONInput):
    """A JSON input for the subarray, built around a dictionary."""

    def __init__(self, json_dict: dict):
        """Initialise the JSON input with a dictionary."""
        super().__init__()
        self._json_dict = json_dict

    def get_json_string(self) -> str:
        """Return the JSON string representation of the input."""
        return json.dumps(self._json_dict)
