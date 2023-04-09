from ezycore import Manager
from ezycore.models import Config, Model, PartialRef


class User(Model):
    id: int
    username: str

    _config: Config = {
        'search_by': 'id'
    }


class Token(Model):
    id: int
    requests: int
    owner: PartialRef[User]              # PartialRef states value is equal to User.id

    _config: Config = {
        'search_by': 'id',
        'partials': dict(owner='users')  # Partials var reduces runtime complexity
                                         # Simply state which segment field points to
    }


manager = Manager(locations=['users', 'tokens'], models={'users': User, 'tokens': Token})
manager['users'].add({'id': 0, 'username': 'Foo'})
manager['tokens'].add({'id': 0, 'requests': 100, 'owner': 0})


print(manager['tokens'].get(0))
# Token(id=0 requests=100 owner=User(id=0, username='Foo'))
