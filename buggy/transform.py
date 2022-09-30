from functools import partial

from .kobo import Kobo

def mapping_transform(entry_key: str, output_key: str, mapping: dict, default, entry: dict) -> tuple:
    return output_key, mapping.get(entry.get(entry_key), default)

def convert_key_transform(entry_key: str, output_key: str, default, entry: dict) -> tuple:
    return output_key, entry.get(entry_key, default)

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

effort_transform = partial(
    convert_key_transform,
    "session_info/Survey_duration",
    "EwA - Observation Effort-time",
    None
)

quantity_transform = partial(
    convert_key_transform,
    "arthropod_documentation/quantity",
    "EwA - Quantity",
    None
)

length_transform = partial(
    convert_key_transform,
    "arthropod_documentation/length",
    "EwA - Length",
    None
)

wetness_transform = partial(
    convert_key_transform,
    "host_documentation/wet_support",
    "EwA - Wet Host",
    None
)

OBSERVATION_FIELD_TRANSFORMERS = [
    survey_transform,
    development_transform,
    activity_transform,
    host_phenology_transform,
    effort_transform,
    quantity_transform,
    length_transform,
    wetness_transform,
]

def observation_field_transformer(transformers: list, entry: dict) -> tuple:
    observation_fields = {}
    for transformer in transformers:
        key, value = transformer(entry)
        observation_fields[key] = value
    return "observation_fields", observation_fields

def image_transformer(image_fields, entry: dict) -> tuple:
    attachments = {
        info["filename"].split("/")[-1]: info
        for info in entry["_attachments"]
    }
    order = [
        entry[field] 
        for field in image_fields
        if entry.get(field)
    ]
    image_info = [
        {
            "instance": attachments[filename]["instance"],
            "id": attachments[filename]["id"]
        }
        for filename in order
    ]
    return "images", image_info

def longitude_transform(entry: dict) -> tuple:
    return 'longitude', entry['geolocation'][1]

def latitude_transform(entry: dict) -> tuple:
    return 'longitude', entry['geolocation'][0]

def notes_transform(sections: dict, order: list, entry: dict) -> tuple:
    
    assert set(sections) == set(order)
    
    notes = ""
    for field in order:
        header = sections[field]
        if field in entry:
            notes += "\n".join([
                header,
                entry[field],
                "", ""
            ])
    return "notes", notes.strip()

BUGGY_TRANSFORMERS = [
    partial(observation_field_transformer, OBSERVATION_FIELD_TRANSFORMERS),
    partial(
        image_transformer,
        [
            "arthropod_documentation/arthropod_photo_1",
            "arthropod_documentation/arthropod_photo_2",
            "arthropod_documentation/arthropod_photo_3",
            "host_documentation/host_photo"
        ]
    ),
    longitude_transform,
    latitude_transform,
    partial(
        convert_key_transform,
        "session_info/survey_ts",
        "ts",
        None
    ),
    partial(
        notes_transform,
        {
            "session_info/survey_method_other": "Survey Method:",
            "arthropod_documentation/arthropod_group_other": "Arthropod Identification:",
            "arthropod_documentation/developmental_stage_other": "Development Stage:",
            "arthropod_documentation/activity_other": "Behavior:",
            "arthropod_documentation/arthropod_more": "Arthropod Notes:",
            "host_documentation/host_group_other": "Host Identification",
            "host_documentation/host_phenology_other": "Host Phenology",
            "host_documentation/host_more": "Host Notes"
        },
        [
            "session_info/survey_method_other",
            "arthropod_documentation/arthropod_group_other",
            "arthropod_documentation/developmental_stage_other",
            "arthropod_documentation/activity_other",
            "arthropod_documentation/arthropod_more",
            "host_documentation/host_group_other",
            "host_documentation/host_phenology_other",
            "host_documentation/host_more"
        ]
    )
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
