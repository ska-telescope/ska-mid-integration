import json
import os

import pytest

from ska_jupyter_scripting.helpers.qa_metrics import QAMetrics


def test_generate_display_url():
    namespace = "foo"
    qa = QAMetrics(namespace)

    assert qa.generate_display_url() == f"/{namespace}/signal/display/"
