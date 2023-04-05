from ezycore import Config, Manager, Model


class User(Model):
    username: str
    password: str

    _config: Config = Config(search_by='username')

manager = Manager(locations=['users'], models={'users': User})
manager.populate('users',
                 dict(username='Isa', password='Password'),
                 dict(username='Foo', password='p1swe'),
                 dict(username='Bar', password='bar-sfsd')
                )

manager['users'].pretty_print()

foo = manager['users'].get('Foo', 'password')
print(foo)

manager['users'].pretty_print()
