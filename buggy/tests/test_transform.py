import unittest
import httpretty
import json

from buggy import kobo

from ..transform import (
    pull_and_transform_data
)

from ..kobo import Kobo

from ..kobo.tests.test_kobo import register_token_url

class TestPullAndTransformData(unittest.TestCase):

    @httpretty.activate
    def test_simple_transformer(self):
        register_token_url()

        kobo_data = [
            {"field1": 1, "field2": 2},
            {"field1": 3, "field2": 10},
        ]

        httpretty.register_uri(
            httpretty.GET, "https://kf.kobotoolbox.org/api/v2/assets/5678/data.json",
            body=json.dumps({"results": kobo_data})
        )

        kobo = Kobo("user", "1234")
        uid = "5678"

        transformer = lambda entry: ("field", entry["field1"] + entry["field2"])
        transformers = [transformer]

        transformed_data = pull_and_transform_data(kobo, uid, transformers)

        expected_data = [
            {"field": 3},
            {"field": 13}
        ]

        assert transformed_data == expected_data
