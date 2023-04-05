## For different drivers, setting up segments may vary

from ezycore import Manager
from ezycore.drivers import SqliteDriver
from ezycore.models import Model


class UserModel(Model):
    _id: str
    username: str
    password: str


driver = SqliteDriver('my_file.sqlite')
driver.setup_segments(users='user_table')

manager = Manager(locations=['users'], models={'users': UserModel})
manager.populate_using_driver('users', driver=driver)

manager['users'].pretty_print()

manager['users'].add({'_id': 'SomeVeryRandomId', 'username': 'Bob', 'password': 'Ilikecheese123'})

manager.export_segment('users', driver=driver)

driver.refresh()
manager.populate_using_driver('users', driver=driver)
manager['users'].pretty_print()
