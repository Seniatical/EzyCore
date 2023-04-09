## For different drivers, setting up segments may vary

from ezycore import Manager
from ezycore.drivers import SQLiteDriver
from ezycore.models import Config, Model


class UserModel(Model):
    id: int
    username: str
    password: str

    _config: Config = Config(search_by='id')


driver = SQLiteDriver('./test.sqlite', models={'users': UserModel})

manager = Manager(locations=['users'], models={'users': UserModel})
manager.populate_using_driver('users', driver=driver)

manager['users'].pretty_print()

manager['users'].add({'id': 5, 'username': 'Gif', 'password': 'Giffy-5333?'})

manager.export_segment('users', driver=driver)
manager['users'].clear()

manager.populate_using_driver('users', driver=driver)
manager['users'].pretty_print()
