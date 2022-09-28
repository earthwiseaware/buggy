from functools import partial

from .kobo import Kobo

def mapping_transform(entry_key, output_key, mapping, default, entry):
    return output_key, mapping.get(entry.get(entry_key), default)

survey_transform = partial(
    mapping_transform, 
    "session_info/survey_method",
    "EwA - Survey Method",
    {
        "incidental": "Opportunistic encounter",
        "walking": "Semi-structured survey",
        "transect_survey": "Transect survey",
        "area": "Area search",
        "other": "Other"
    },
    "Other"
)

development_transform = partial(
    mapping_transform,
    "arthropod_documentation/developmental_stage",
    "EwA - Arthropod Developmental Stage",
    {
        "adult": "Adult",
        "egg": "Egg or eggsac",
        "larva": "Larva or caterpillar",
        "pupa": "Pupa",
        "nymph": "Nymph",
        "other": "Other"
    },
    "Other"
)

activity_transform = partial(
    mapping_transform,
    "arthropod_documentation/activity",
    "EwA - Behavior Observed",
    {
        "mating": "Mating",
        "moving": "Moving",
        "foraging": "Foraging",
        "feeding": "Feeding",
        "resting": "Resting",
        "predator": "Preying",
        "prey": "Preyed upon",
        "guarding": "Guarding eggs or younglings",
        "tending": "Tending",
        "other": "Other"
    },
    "Other"
)

host_phenology_transform = partial(
    mapping_transform,
    "host_documentation/host_phenology",
    "EwA - Plant Phenology",
    {
        "initial": "Initial growth",
        "breaking": "Breaking leaf buds",
        "increasing": "Increasing leaf size",
        "flowers": "Flowers",
        "fruiting": "Fruits",
        "mature": "Leaves",
        "other": "Other"
    },
    "Other"
)

BUGGY_TRANSFORMERS = [
    survey_transform,
    development_transform,
    activity_transform,
    host_phenology_transform,
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
