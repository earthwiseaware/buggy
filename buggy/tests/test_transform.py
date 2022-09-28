import unittest
import httpretty
import json

from functools import partial

from ..transform import (
    pull_and_transform_data,
    mapping_transform
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

class TestMappingTransform(unittest.TestCase):
    def setUp(self):
        entry_key = "survey_field"
        output_key = "output_field"
        mapping = {
            "good_value": "good",
        }
        default = "missing"
        self.transformer = partial(
            mapping_transform, entry_key,
            output_key, mapping, default
        )

    def test_entry_key_present(self):
        assert self.transformer({"survey_field": "good_value"}) == ("output_field", "good")

    def test_entry_key_missing(self):
        assert self.transformer({}) == ("output_field", "missing")

    def test_mapping_key_missing(self):
        assert self.transformer({"survey_field": "bad_value"}) == ("output_field", "missing")
