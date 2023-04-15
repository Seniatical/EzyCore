.. meta::
   :title: EzyCore - Documentation [Guides]
   :type: website
   :url: https://ezycore.readthedocs.io
   :description: Read more about how cache invalidation works in EzyCore
   :theme-color: #f54646

******************
Cache Invalidation
******************
Automated cache invalidation has never been simpler in EzyCore

Segments At Max Cap
-------------------
When a segment has reached maximum capacity, if :attr:`BaseSegment.make_space` is ``True``,
EzyCore will automatically begin removing items from the cache starting from the items which are least accessed.

For segments such as our default implementation. 
You can see if the last item fetched was invalidated via :attr:`Segment._invalidated_last`

.. code-block:: diff
    
      # manager/segment.py -> Segment.__init__
      # self.__queue holds order of keys from least accessed -> recently accessed
      # So __queue[0] == least accessed and __queue[-1] == most recently accessed
    + self.__queue = list()
    + self.__data = dict()

Fetching items
==============
When an item is fetched via :meth:`BaseSegment.get` EzyCore will move the item to the back of the queue

.. code-block:: diff

      # manager/segment.py -> Segment.get
    + self.__queue.remove(obj_key)
      # ValueError indicates item doesn't exist
    + self.__queue.append(obj_key)
      # Move key to the front of queue

Adding Items
============
First we check if cap has been reached, before we remove objects.

.. code-block:: diff

      # manager/segment.py -> Segment.add
      # Check if cap reached
    + if (len(self.__queue) >= self.max_size) and (self.max_size > 0):
      # Then if make_space is True we remove the first item in __queue
    + k = self.__queue.pop(0)
      # Then remove from data
    + self.__data.pop(k)

     # Then we can safely add new item

Following :attr:`Model.invalidate_after`
----------------------------------------
Optionally we can say to invalidate an element after it has been accessed `n` times.

.. code-block:: py

    class AccessOneTime(Model):
        otp: str
        user_id: int

        _config: Config = {
            'search_by': 'otp',
            'invalidate_after': 1
        }

User Implementations
====================
Tracking the number of times we have accessed a recourse can be done via,
:attr:`Config.__ezycore_internal__` and using the key ``n_fetch``.

.. tip::

    Once a model has been invalidated we usually leave ``n_fetch`` as it is,
    so when they try to re-add the same model we can say it was previously invalidated.

    .. code-block:: diff

          # manager/segment.py -> Segment.add
        + if isinstance(obj, self.model):
        +   if obj._config.__ezycore_internal__['n_fetch'] >= obj._config.invalidate_after:
        +     raise ValueError('Item has already been invalidated')

.. code-block:: diff

      # manager/segment.py -> Segment.get
    + max_fetches = result._config.invalidate_after
    + if max_fetches < 0:
    +   self._invalidated_last = False
    +   return result
    + 
    + fetches = result._config.__ezycore_internal__['n_fetch'] + 1
    + if fetches >= max_fetches:
    +   self._invalidated_last = True
    +   self.remove(obj_key)
    + else:
    +   self._invalidated_last = False
    +   result._config.__ezycore_internal__['n_fetch'] = fetches
    + return value

Using :meth:`BaseSegment.invalidate_all`
----------------------------------------
We can optionally remove all elements that pass a check function using, :meth:`BaseSegment.invalidate_all`

.. note::
    
    When implementing your own ``invalidate_all`` func it is highly recomended to identify all items,
    before removing them to eliminate any unexpected errors.

Definition
==========
.. code-block:: py

    invalidate_all(self, func: Callable[[Model], bool], *, limit: int = -1) -> Iterable[Model]:

when ``func(element)`` returns ``True`` we remove the item from cache,
once we remove `n` items where ``n >= limit`` we stop invalidating.

.. note::
    if ``limit < 0`` we dont stop for when ``n >= limit``,
    we continue till we reach the end of the segment
