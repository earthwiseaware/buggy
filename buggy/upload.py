import os

from tqdm import tqdm

from gluon.inaturalist.client import iNaturalistClient as iNaturalist
from gluon.kobo.client import KoboClient as Kobo

def upload_data(data: dict, uid: str, inaturalist_client: iNaturalist, kobo_client: Kobo) -> None:
    for record in tqdm(data):
        if not record['is_valid']: continue

        # start by downloading the images
        image_paths = []
        instance = record['instance']
        for image in record['images']:
            image_path = f'{uid}_{instance}_{image}'
            kobo_client.pull_image(
                image_path, uid, instance, image
            )
            image_paths.append(image_path)
        
        # upload the base observation
        observation_id = inaturalist_client.upload_base_observation(
            record['taxa'], 
            record['longitude'], 
            record['latitude'], 
            record['ts'], 
            record['positional_accuracy'], 
            record['notes']
        )

        # attach the images
        for image_path in image_paths:
            inaturalist_client.attach_image(
                observation_id, image_path
            )
            os.remove(image_path)

        # attach the observation field values
        for field_id, value in record['observation_fields']:
            inaturalist_client.attach_observation_field(
                observation_id, field_id, value
            )
