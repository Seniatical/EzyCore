# EzyCore
A highly customizable cache manager for python

#### Why use EzyCore
* Implements proper data structures thanks to PyDantic
* Supports partial referencing, easy updates across multiple caches/tables
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
```
<p>
    View more examples over <a href="/tree/main/examples">here</a>!
</p>
