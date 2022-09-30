# buggy
ETLs for buggy

```python
import json

from getpass import getpass

from buggy.kobo import Kobo
from buggy.transform import (
    pull_and_transform_data,
    BUGGY_TRANSFORMERS
)
from buggy.identifier import FANIdentifier

identifier = FANIdentifier('db.json')
kobo = Kobo("mgietzmann", getpass())
uid = "aMY6fQPkiQrzkSgq5G6gSC" #"aSBPGGHRp74nBwVVPt28vF"
transformed, failed = pull_and_transform_data(
    kobo, uid,
    BUGGY_TRANSFORMERS,
    identifier=identifier
)

print(f"{failed} Failed...")
with open("data.json", "w") as fh:
    json.dump(
        transformed, fh, 
        sort_keys=True, 
        indent=4
    )
```
