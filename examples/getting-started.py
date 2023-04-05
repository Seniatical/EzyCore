from ezycore import Manager
from ezycore.models import Model, Config
from os import urandom


## First we define our model were going to use
## All objects stored in the 'users' segment will follow this schema
class UserModel(Model):
    id: str
    username: str
    password: str

    _config: Config = {
        'search_by': 'id',
    }

    @classmethod
    def random(cls) -> "UserModel":
        return cls(id=urandom(10).hex(), username=urandom(5).hex(), password=urandom(20).hex())


## Create our manager
manager = Manager(locations=['users'], models={'users': UserModel})

## Populate users segment with some data
## 5 unknown values and 1 we know
manager.populate(location='users', 
                 data=[UserModel.random() for _ in range(5)] + [UserModel(id='user_id', username='foo', password='apassword')])


## Finding user in Cache
print(manager['users'].get('user_id'))
### Using flags to fetch specific data
# manager['users'].get('user_id', '*')  -> fetches as a dict instead of UserModel
# manager['users'].get('user_id', '_id', 'username') -> fetches only _id and username
# manager['users'].get('user_id', exclude={'password'}) -> excludes password from result

## Updating user in Cache
manager['users'].update('user_id', username='bar')
print(manager['users'].get('user_id'), '\n')

## Deleting user in Cache
manager['users'].remove('user_id')

manager['users'].pretty_print()
