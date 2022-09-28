from functools import partial

from .kobo import Kobo

def mapping_transform(entry_key, output_key, mapping, default, entry):
    return output_key, mapping.get(entry.get(entry_key), default)

survey_method_entry_key = "session_info/survey_method"
survey_method_output_key = "survey_method"
survey_method_mapping = {
    "incidental": "Opportunistic encounter",
    "walking": "Semi-structured survey",
    "transect": "Transect survey",
    "area": "Area search",
    "other": "Other"
}
survey_method_default = "Other"
survey_method_transform = partial(
    mapping_transform, survey_method_entry_key,
    survey_method_output_key, survey_method_mapping, 
    survey_method_default
)

BUGGY_TRANSFORMERS = [
    survey_method_transform,
]

def pull_and_transform_data(kobo: Kobo, uid: str, transformers: list) -> dict:
    data = kobo.pull_data(uid)
    transformed_data = []
    for entry in data:
        transformed = {}
        for transformer in transformers:
            key, value = transformer(entry)
            transformed[key] = value
        transformed_data.append(transformed)
    return transformed_data
