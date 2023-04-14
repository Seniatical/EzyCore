.. meta::
   :title: EzyCore - Documentation
   :type: website
   :url: https://ezycore.readthedocs.io
   :description: Welcome to EzyCore's Documentation
   :theme-color: #f54646

Welcome to EzyCore's documentation!
===================================

Welcome to the EzyCore module documentation! EzyCore is a powerful and customizable cache manager for Python, 
designed to help you optimize the performance of your code. With built-in support for pydantic, 
EzyCore makes it easy to keep your data structured and organized. In this documentation, 
you'll find everything you need to get started with EzyCore, including installation instructions, 
usage examples, and configuration options. 

We hope you find EzyCore to be a valuable addition to your Python toolbox!


Why Use EzyCore
===============

* Enforces use of proper structured data thanks to PyDantic
* Comes with out of box support for many popular databases such as SQLite3 and more!
* Built on strict ABC classes, supports flexibility and community made objects!
* Fast efficient and easy to use

Installation
============
As of now EzyCore is in its development stage, therefore installation must be done via github

.. code-block:: sh

   pip install git+https://github.com/Seniatical/EzyCore/

Basic Example
=============

.. code-block:: py

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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   module.rst
   models.rst
   guides/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
