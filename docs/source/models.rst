.. meta::
   :title: EzyCore - Documentation [Models Reference]
   :type: website
   :url: https://ezycore.readthedocs.io/models.html
   :description: Models reference for EzyCore
   :theme-color: #f54646

.. currentmodule:: ezycore

******
Models
******
EzyCore uses ``Pydantic`` for handling its models,
this provides us with many advantages such as stronger validation methods.

All `Model` like objects in the EzyCore library must inherit the :class:`Model` class.


What is the :class:`Model` class?
---------------------------------
The `Model` class is simply an extended version of pydantic's ``BaseModel`` class,
It offers all the same features as it does and works virtually the same.

What does the :class:`Model` class do?
--------------------------------------
* Ensures a ``_config`` variable exists, which helps customise how segments/managers behave
* Verifies all partial references within an object

Controlling :meth:`BaseSegment.get`
-----------------------------------

.. code-block:: py
    :caption: Returning all fields except ``_config`` as dict

    [BaseSegment].get(..., '*')
    # Ignores any other kwds provided!!!

.. code-block:: py
    :caption: Returns only fields ``f1`` and ``f2``

    [BaseSegment].get(..., 'f1', 'f2')

.. code-block:: py
    :caption: Includes ``f1.f2`` and ``f3``

    [BaseSegment].get(..., ('f1', {'f2': True}), 'f3')

.. code-block:: py
    :caption: Normal pydantic kwargs also work

    [BaseSegment].get(..., exclude_none=True)
    # Ignore any fields set to "None"

Examples
--------

Basic
~~~~~
A basic user object which excludes fields ``_config`` and ``password`` when fetched

.. code-block:: py

    class User(Model):
        id: int
        username: str
        password: str
        created_at: datetime.datetime
        updated_at: datetime.datetime

        _config: Config = dict(search_by='id', exclude={'_config', 'password'})


Intermediate
~~~~~~~~~~~~
Implements partial referencing to fetch results from the ``users`` segment

.. code-block:: py

    class Token(Model):
        id: int
        limit: int
        used: int 
        created_at: datetime.datetime
        updated_at: datetime.datetime
        owner: PartialRef[User]

        _config: Config = dict(
            search_by='id', 
            exclude={'_config': True, 'user': {'password'}}
            partials={'owner': 'users'})

References
----------

Config
~~~~~~
.. autoclass:: ezycore.models.Config
    :members:
    :inherited-members:

Model
~~~~~
.. autoclass:: ezycore.models.Model
    :members:
    :inherited-members:
