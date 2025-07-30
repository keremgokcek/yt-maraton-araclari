from quart_auth import AuthUser
from json import load


class User(AuthUser):
    def __init__(self, auth_id):
        super().__init__(auth_id)
        self._username = None

        if not auth_id:
            return

        logins = load(open('logins.json'))
        for user, data in logins.items():
            if data['id'] == auth_id:
                self._username = user
                return

        print(f'WARNING: User with id {auth_id} not found!')

    @property
    def username(self):
        return self._username
