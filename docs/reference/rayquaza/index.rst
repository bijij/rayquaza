.. currentmodule:: rayquaza


Mediator
========

.. autoclass:: Mediator
    :members:

Message
=======

.. autoclass:: Message()
    :members:

Request
=======

.. autoclass:: Request()
    :members:

.. class:: SingleResponseRequest[ResponseT]

    A request that expects a single response.

    An alias for :class:`Request` with the :class:`RequestType` set to :attr:`RequestType.single`.

    Example:

    .. code-block:: python

        class SetVolumeRequest(SingleResponseRequest[SetVolumeResponse]):
            def __init__(self, volume: float) -> None:
                self.volume: float = volume


.. class:: MultiResponseRequest[ResponseT]
    
    A request that can have multiple responses.

    An alias for :class:`Request` with the :class:`RequestType` set to :attr:`RequestType.multi`.

    Example:

    .. code-block:: python

        class GetListenersRequest(MultiResponseRequest[Listener]):
            pass

    .. note::

        The responses are sent as they are generated, so the order of the responses is not guaranteed.

    .. tip::

        Handlers may choose to return ``None`` to indicate that they have no response to send. In this scenario the requester will not be notified of the response.


.. autoclass:: RequestType()
    :members:

Exceptions
==========

.. autoclass:: MessagePublishedException
    :members:

.. autoclass:: UnqualifiedRequestTypeException
    :members:

.. autoclass:: BadResponseError
    :members:

.. autoclass:: NoActiveSubscribersException
    :members: