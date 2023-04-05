from ezycore import Manager
from ezycore.models import Model, Config
from os import urandom


class UserModel(Model):
    _id: str
    username: str
    password: str

    __config__: Config = {
        'search_by': '_id',
    }

    @classmethod
    def random(cls) -> "UserModel":
        return cls(id=urandom(10).hex(), username=urandom(5).hex(), password=urandom(20).hex())


manager = Manager(locations=['users'], models={'users': UserModel})
manager.populate(location='users', 
                 data=[UserModel.random() for _ in range(5)] + [UserModel(_id='user_id', username='foo', password='apassword')])

## Finding user in Cache
print(manager['users'].get('user_id'))
### Using flags to fetch specific data
# manager['users'].get('user_id', '*')  -> fetches as a dict instead of UserModel
# manager['users'].get('user_id', '_id', 'username') -> fetches only _id and username
# manager['users'].get('user_id', exclude={'password'}) -> excludes password from result

## Updating user in Cache
manager['users'].update('user_id', username='bar')
print(manager['users'].get('user_id'))
## Deleting user in Cache
manager['users'].remove('user_id')

manager['users'].pretty_print()
