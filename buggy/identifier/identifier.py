import json

from random import choice

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMERIC = "0123456789"

# Four digit, Alpha Numeric Identifier
class FANIdentifier(object):
    def __init__(self, db: str) -> None:
        self.db = db
        with open(db, "r") as fh:
            self.db_content = json.load(fh)

    def _check_for_user(self, user_kobo_id: str) -> bool:
        return user_kobo_id in self.db_content

    def _add_user(self, user_kobo_id: str) -> None:
        claimed_ids = set(self.db_content.values())
        already_claimed = True
        while already_claimed:
            proposed_id = ''.join([
                choice(ALPHA),
                choice(ALPHA),
                choice(NUMERIC),
                choice(NUMERIC)
            ])
            already_claimed = proposed_id in claimed_ids
        self.db_content[user_kobo_id] = proposed_id
        with open(self.db, 'w') as fh:
            json.dump(self.db_content, fh, sort_keys=True, indent=4)

    def _get_identifier(self, user_kobo_id: str) -> str:
        return self.db_content[user_kobo_id]

    def get_identifier(self, user_kobo_id: str) -> str:
        if not self._check_for_user(user_kobo_id):
            self._add_user(user_kobo_id)
        return self._get_identifier(user_kobo_id)
