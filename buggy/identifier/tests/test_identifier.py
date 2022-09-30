import unittest
import os
import json

from time import time

from ..identifier import (
    FANIdentifier
)

class TestFANIdentifier(unittest.TestCase):
    def test_check_user(self):
        db = f"db_{int(time())}.json"
        with open(db, "w") as fh:
            json.dump(
                {"garlicbread@geemail.com": "AX12"},
                fh
            )

        try:
            identifier = FANIdentifier(db)
            assert identifier._check_for_user("garlicbread@geemail.com")
            assert not identifier._check_for_user("garlicknots@geemail.com")
            os.remove(db)
        except Exception as e:
            os.remove(db)
            raise e

    def test_add_user(self):
        db = f"db_{int(time())}.json"
        with open(db, "w") as fh:
            json.dump(
                {"garlicbread@geemail.com": "AX12"},
                fh
            )

        try:
            identifier = FANIdentifier(db)
            identifier._add_user("garlicknots@geemail.com")
            with open(db, 'r') as fh:
                content = json.load(fh)
            assert "garlicknots@geemail.com" in content
            os.remove(db)
        except Exception as e:
            os.remove(db)
            raise e

    def test_get_identifier(self):
        db = f"db_{int(time())}.json"
        with open(db, "w") as fh:
            json.dump(
                {"garlicbread@geemail.com": "AX12"},
                fh
            )

        try:
            identifier = FANIdentifier(db)
            assert identifier._get_identifier("garlicbread@geemail.com") == 'AX12'
            os.remove(db)
        except Exception as e:
            os.remove(db)
            raise e
