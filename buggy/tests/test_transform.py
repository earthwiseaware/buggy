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
    image_transformer,
    identifier_transform
)

from gluon.kobo.client import KoboClient as Kobo

def register_token_url():
    httpretty.register_uri(
        httpretty.GET, "https://kf.kobotoolbox.org/token?format=json",
        body=json.dumps({"token": "what are you token about?"})
    )

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

        transformed_data, failed = pull_and_transform_data(kobo, uid, transformers)

        expected_data = [
            {"field": 3},
            {"field": 13}
        ]

        assert transformed_data == expected_data
        assert failed == 0

    @httpretty.activate
    def test_kwargs_passed(self):
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

        def transformer(entry: dict, **kwargs) -> tuple:
            return "field", kwargs["to_pass"]
        transformers = [transformer]

        transformed_data, failed = pull_and_transform_data(kobo, uid, transformers, to_pass="check for me")

        expected_data = [
            {"field": "check for me"},
            {"field": "check for me"}
        ]

        assert transformed_data == expected_data
        assert failed == 0

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
            output_key, str, default
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
                str,
                None
            )
        ]
        entry = {
            "survey_field": "good_value"
        }
        result = observation_field_transformer(observation_field_transformers, entry)

        assert result == ('observation_fields', {"output_field": "good_value"})

    def test_kwargs_passed(self):
        def transformer(entry: dict, **kwargs) -> tuple:
            return "field", kwargs["to_pass"]
        observation_field_transformers = [
            transformer
        ]
        entry = {
            "survey_field": "good_value"
        }
        result = observation_field_transformer(observation_field_transformers, entry, to_pass="check for me")

        assert result == ('observation_fields', {"field": "check for me"})

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
            4, 2
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

class FakeIdentifier(object):
    @staticmethod
    def get_identifier(user_id):
        return "a user id"

class TestIdentifierTransform(unittest.TestCase):
    def test_entry_key_present(self):
        transform = partial(
            identifier_transform,
            "user_id",
            "identifier"
        )
        entry = {"user_id": "me@geemail.com"}
        assert transform(entry, identifier=FakeIdentifier()) == ("identifier", "a user id")

    def test_entry_key_missing(self):
        transform = partial(
            identifier_transform,
            "user_id",
            "my_identifier"
        )
        entry = {}
        assert transform(entry, identifier=FakeIdentifier()) == ("my_identifier", None)
