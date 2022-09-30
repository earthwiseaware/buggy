import unittest
import httpretty
import json

from functools import partial

from ..transform import (
    notes_transform,
    pull_and_transform_data,
    mapping_transform,
    convert_key_transform,
    observation_field_transformer,
    image_transformer
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

class TestConvertKeyTransform(unittest.TestCase):
    def setUp(self):
        entry_key = "survey_field"
        output_key = "output_field"
        default = "missing"
        self.transformer = partial(
            convert_key_transform, entry_key,
            output_key, default
        )

    def test_entry_key_present(self):
        assert self.transformer({"survey_field": "good_value"}) == ("output_field", "good_value")

    def test_entry_key_missing(self):
        assert self.transformer({}) == ("output_field", "missing")

class TestObservationFieldTransformer(unittest.TestCase):
    def test_base_case(self):
        observation_field_transformers = [
            partial(
                convert_key_transform,
                "survey_field",
                "output_field",
                None
            )
        ]
        entry = {
            "survey_field": "good_value"
        }
        result = observation_field_transformer(observation_field_transformers, entry)

        assert result == ('observation_fields', {"output_field": "good_value"})

class TestImageTransformer(unittest.TestCase):
    def test_base_case(self):
        entry = {
            "photo1": "bug.png",
            "photo3": "plant.png",
            "_attachments": [
                {
                    "filename": "a/long/url/bug.png",
                    "instance": 1,
                    "id": 2
                },
                {
                    "filename": "a/long/url/plant.png",
                    "instance": 3,
                    "id": 4
                },
                {
                    "filename": "a/long/url/other.txt",
                    "instance": 5,
                    "id": 6
                }
            ]
        }
        result = image_transformer(["photo3", "photo2", "photo1"], entry)
        expected = [
            {"instance": 3, "id": 4},
            {"instance": 1, "id": 2}
        ]
        assert result[0] == "images"
        assert result[1] == expected


NOTE = """
The Thing They Forgot:
I had a great time. :)

My Notes:
Hello there!
""".strip()
class TestNotesTransform(unittest.TestCase):
    def test_base_case(self):
        entry = {
            "my note": "Hello there!",
            "postscript": "I had a great time. :)"
        }
        transformer = partial(
            notes_transform,
            {
                "my note": "My Notes:",
                "postscript": "The Thing They Forgot:",
                "other stuff": "Other:"
            },
            [
                "postscript",
                "other stuff",
                "my note"
            ]
        )
        key, transformed = transformer(entry)
        assert key == "notes"
        assert transformed == NOTE