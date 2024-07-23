"""A JSON input based on a file contained in the test data folder."""

import os
from typing import Any

from tests.test_harness3.telescope_inputs.dict_json_input import DictJSONInput
from tests.test_harness3.telescope_inputs.json_input import JSONInput


class FileJSONInput(JSONInput):
    """A JSON input based on a file contained in the test data folder."""

    PATH_TO_TEST_DATA_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "..",
        # "..",
        # "..",
        "data",
    )
    FILE_SUFFIX = ".json"

    def __init__(self, target_file_folder_name: str, target_file_slug: str):
        """Initialize the JSON input with the target file slug.

        :param target_file_folder_name: The target file folder name
            (e.g. "subarray").
        :param target_file_slug: The target file slug (e.g. "configure_mid").
        """
        self.target_file_folder_name = target_file_folder_name
        self.target_file_slug = target_file_slug

    def filename(self) -> str:
        """Return the filename of the JSON input.

        :return: The filename of the JSON input, built combining the target
            file folder name and the target file slug (together also with the
            test data folder path).
        """
        return os.path.join(
            self.PATH_TO_TEST_DATA_FOLDER,
            self.target_file_folder_name,
            f"{self.target_file_slug}{self.FILE_SUFFIX}",
        )

    def get_json_string(self):
        with open(self.filename(), "r") as file:
            json_string = file.read()
        return json_string

    def set_attribute_value(
        self, attr_name: str, attr_value: Any
    ) -> "DictJSONInput":
        new_json_dict = self.get_json_dict()
        new_json_dict[attr_name] = attr_value
        return DictJSONInput(new_json_dict)
