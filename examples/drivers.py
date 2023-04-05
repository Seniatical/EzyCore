## For different drivers, setting up segments may vary

from ezycore import Manager
from ezycore.drivers import SqliteDriver
from ezycore.models import Config, Model


class UserModel(Model):
    id: str
    username: str
    password: str

    _config = Config(search_by='id')


driver = SqliteDriver('my_file.sqlite')
driver.setup_segments(users='user_table')

manager = Manager(locations=['users'], models={'users': UserModel})
manager.populate_using_driver('users', driver=driver)

manager['users'].pretty_print()

manager['users'].add({'id': 'SomeVeryRandomId', 'username': 'Bob', 'password': 'Ilikecheese123'})

manager.export_segment('users', driver=driver)

driver.refresh()
manager.populate_using_driver('users', driver=driver)
manager['users'].pretty_print()
