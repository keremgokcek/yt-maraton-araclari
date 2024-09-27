from quart_auth import AuthUser
from orjson import loads


class User(AuthUser):
    def __init__(self, auth_id):
        super().__init__(auth_id)
        self.id = auth_id
        self._username = None
       
    async def set_username(self):
        with open('logins.json') as f:
            logins = loads(f.read())
            
        for user, data in logins.items():
            if data['id'] == self.id:
                self._username = user
                break
        
    @property
    async def username(self):
        await self.set_username()
        return self._username
