# EzyCore
A highly customizable cache manager for python

### Why use EzyCore
* Implements proper data structures using pydantic 
* Supports partial referencing between caches
* Out of box support for many popular databases, such as SQLite, MongoDB and MySQL
* Built on strict ABC classes, allows tons of flexibility and code customisation

## Example
```py
from ezycore import Config, Manager, Model


class Message(Model):
    id: int
    content: str
    author: str

    _config: Config = {'search_by': 'id'}

manager = Manager(locations=['messages'], models={'messages': Message})
manager['messages'].add({'id': 123, 'content': 'Foo', 'author': 'Foo'})

print(manager['messages'].get(123))
# Message(id=123, content='Foo', author='Foo')
```
<p>
    View more examples over <a href="/examples">here</a>!
</p>
