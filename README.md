<p align="center">
    <img src="/docs/source/_static/el_l2_nws.png">
</p>

***

<h3 align="center">A highly customisable cache manager for python</h3>

# Why choose EzyCore
* Enforces use of proper structured data thanks to PyDantic
* Comes with out of box support for many popular databases such as **SQLite3** and more!
* Built on strict ABC classes, supports flexibility and community made objects!
* Fast efficient and easy to use

# Installation
```sh
pip install git+https://github.com/Seniatical/EzyCore
```

# Basic Example
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

# Documentation
<p>
    Learn more about about our module by visiting our docs <a href="http://ezycore.rtfd.io/">here</a>!
</p>
