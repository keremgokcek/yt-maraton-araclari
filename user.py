from quart_auth import AuthUser
from tools import get_user_data
from json import load


class User(AuthUser):
    def __init__(self, auth_id):
        super().__init__(auth_id)
        self.id = auth_id
        self._username = None
       
    async def set_username(self):
        with open('logins.json') as f:
            logins = load(f)
            
        for user, data in logins.items():
            if data['id'] == self.id:
                self._username = user
                break
        
    @property
    async def username(self):
        await self.set_username()
        return self._username
