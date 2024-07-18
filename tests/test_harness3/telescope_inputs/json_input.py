"""Template for a generic JSON input."""

import abc
import json


class JSONInput(abc.ABC):
    """Template for a generic JSON input..

    This class is an abstract class that defines a template for a JSON input
    for a command over the telescope. It can be used to create a JSON input
    for various ``TelescopeAction``s.
    """

    @abc.abstractmethod
    def get_json_string(self) -> str:
        """Return the JSON string representation of the input."""
        pass

    def get_json_dict(self) -> dict:
        """Return the JSON dictionary representation of the input."""
        return json.loads(self.get_json_string())

    def is_equal_to_json(self, other_json: str | dict) -> bool:
        """Check if the JSON input is equal to another JSON string or dict."""
        if isinstance(other_json, str):
            return self.get_json_string() == other_json
        return self.get_json_dict() == other_json

    def __str__(self) -> str:
        """Return the JSON string representation of the input."""
        return self.get_json_string()

    def __repr__(self) -> str:
        """Return the JSON string representation of the input."""
        return self.get_json_string()

    def __eq__(self, other: object) -> bool:
        """Check if two JSON inputs are equal."""
        return self.get_json_dict() == other.get_json_dict()
