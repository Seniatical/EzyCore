from ezycore import Manager, Model, Config
from enum import IntFlag


class Grant(IntFlag):
    MODIFY = 1 << 0
    CREATE = 1 << 1
    REMOVE = 1 << 2


class SecureRecourse(Model):
    code: str
    grants: Grant
    super_secret_key: str
    
    _config: Config = {
        'search_by': 'code',
        'invalidate_after': 1
    }

manager = Manager(locations=['codes'], models={'codes': SecureRecourse})
manager['codes'].add({'code': '#12345', 'grants': Grant.MODIFY | Grant.CREATE, 'super_secret_key': 'MyKey123'})

print(manager['codes'].get('#12345').json(indent=4))
# {
#     "code": "#12345",
#     "grants": 3,
#     "super_secret_key": "MyKey123"
# }

try:
    print(manager['codes'].get('#12345'))
    # ValueError: Object doesn't exist
except ValueError as err:
    print('Error:', err.args[0])
print(manager['codes']._invalidated_last)
# True
