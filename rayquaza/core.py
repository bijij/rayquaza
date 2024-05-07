from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterable, Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeVar, overload

from .exception import BadResponseError, MessagePublishedException, UnqualifiedRequestTypeException
from .model import Message, Request, RequestType

if TYPE_CHECKING:
    from .model import SingleResponseRequest, MultiResponseRequest
    from .types import T_MSG

from .utils import MISSING

T = TypeVar("T")

__all__ = ("Mediator",)


class Mediator:
    """The mediator class that handles message passing between components."""

    def __init__(self) -> None:
        self._callbacks: dict[type[Message], set[Callable[[Message], Coroutine[Any, Any, Any]]]] = defaultdict(set)

    async def publish(self, message: Message, /, *, wait: bool = True, timeout: float | None = None) -> None:
        """|coro|

        Publishes a message to the mediator.

        Parameters
        ----------
        message: :class:`Message`
            The message to publish.
        wait: :class:`bool`
            Whether to wait for the callbacks to finish executing.
        timeout: Optional[:class:`float`]
            The maximum time to wait for the callbacks to finish executing.
            Only applicable if ``wait`` is set to ``True``.

        Raises
        ------
        :class:`ValueError`
            The ``timeout`` parameter was set without setting ``wait`` to ``True``.
        :class:`MessagePublishedException`
            The message has already been published.
        :class:`asyncio.TimeoutError`
            The timeout was reached while waiting for the callbacks to finish executing.
        """
        if not wait and timeout is not None:
            raise ValueError("timeout can only be set if wait is True")

        if message.__mediator_published__:
            raise MessagePublishedException(message)

        if wait:
            coros = (callback(message) for callback in self._callbacks[message.__class__])
            await asyncio.wait_for(asyncio.gather(*(coros)), timeout)
        else:
            for callback in self._callbacks[message.__class__]:
                asyncio.create_task(callback(message))

    async def has_subscriptions(self, message_type: type[Message]) -> bool:
        """Checks if the mediator has any subscriptions for a message type.

        Parameters
        ----------
        message_type: type[:class:`Message`]
            The type of message to check for subscriptions.

        Returns
        -------
        :class:`bool`
            Whether the mediator has any subscriptions for the message type.
        """
        return bool(self._callbacks[message_type])

    async def _single_response_request(self, message: SingleResponseRequest[T], timeout: float | None) -> T:
        if not await self.has_subscriptions(message.__class__):
            raise RuntimeError(f"Request of type {message.__class__} has no active subscriptions.")

        response_type: type[T] = message.__mediator_response_type__
        (callback,) = self._callbacks[message.__class__]
        response = await asyncio.wait_for(callback(message), timeout)
        # if not isinstance(response, response_type):
        #     raise BadResponseError(message, response, response_type)
        return response

    async def _multi_response_request(self, message: MultiResponseRequest[T], timeout: float | None) -> AsyncIterable[T]:
        response_type: type[T] = message.__mediator_response_type__
        callbacks = self._callbacks[message.__class__]
        for coro in asyncio.as_completed([callback(message) for callback in callbacks], timeout=timeout):
            response = await coro
            if response is None:
                continue
            # if not isinstance(response, response_type):
            #     raise BadResponseError(message, response, response_type)
            yield response

    @overload
    def request(self, message: SingleResponseRequest[T], timeout: float | None = None) -> Coroutine[Any, Any, T]: ...

    @overload
    def request(self, message: MultiResponseRequest[T], timeout: float | None = None) -> AsyncIterable[T]: ...

    def request(self, message: Request[T, Any], timeout: float | None = None) -> Coroutine[Any, Any, T] | AsyncIterable[T]:
        """|coro|

        Send a request to the mediator and return the response or responses.

        Examples

        .. code-block:: python

            # Single response request
            response = await mediator.request(SetVolumeRequest(volume=0.5))
            print(response)

            # Multi response request
            async for response in mediator.request(GetListenersRequest()):
                print(response)

        Parameters
        ----------
        message: :class:`Request`
            The request to send.
        timeout: Optional[:class:`float`]
            The maximum time to wait for the response.

        Raises
        ------
        :class:`RuntimeError`
            The message has already been published.
        :class:`UnqualifiedRequestTypeException`
            The request type is unqualified.
        :class:`BadResponseError`
            The response type does not match the expected response type.
        :class:`NoActiveSubscribersException`
            There are no active subscriptions for the request type.
        :class:`asyncio.TimeoutError`
            The timeout was reached while waiting for the response.

        Returns
        -------
        ``Any``
            The response if the request was a :attr:`RequestType.single` request.

        Yields
        ------
        ``Any``
            The responses if the request was a :attr:`RequestType.multi` request.
        """
        if message.__mediator_published__:
            raise MessagePublishedException(message)

        if message.__mediator_request_type__ is MISSING:
            raise UnqualifiedRequestTypeException(message)

        if message.__mediator_request_type__ is RequestType.single:
            return self._single_response_request(message, timeout)

        return self._multi_response_request(message, timeout)

    @overload
    def create_subscription(
        self,
        message_type: type[MultiResponseRequest[T]],
        callback: Callable[[Message], Coroutine[Any, Any, T | None]],
    ) -> None: ...

    @overload
    def create_subscription(
        self,
        message_type: type[Request[T, Any]],
        callback: Callable[[Message], Coroutine[Any, Any, T]],
    ) -> None: ...

    @overload
    def create_subscription(
        self,
        message_type: type[T_MSG],
        callback: Callable[[T_MSG], Coroutine[Any, Any, Any]],
    ) -> None: ...

    def create_subscription(
        self,
        message_type: type[T_MSG],
        callback: Callable[[T_MSG], Coroutine[Any, Any, Any]],
    ) -> None:
        """Registers a subscription for a message type.

        Parameters
        ----------
        message_type: type[:class:`Message`]
            The type of message to subscribe to.

        callback: Callable[[:class:`Message`], Coroutine[Any, Any, Any]]
            The callback to execute when a message of the specified type is published.
            In the case of a request, the callback should return the appropriate response.

        Raises:
        -------
        :class:`TypeError`
            The message type is not a subclass of :class:`Message`.
        :class:`RuntimeError`
            The request type is :attr:`RequestType.single` and already has a subscription.
        """
        if not issubclass(message_type, Message):
            raise TypeError("message_type must be a subclass of Message")

        if (
            issubclass(message_type, Request)
            and message_type.__mediator_request_type__ is RequestType.single
            and self._callbacks[message_type]
        ):
            raise RuntimeError("Request type already has a subscription")

        self._callbacks[message_type].add(callback)  # type: ignore  # I'm not sure why this is an error

    def unsubscribe(
        self, message_type: type[Message], callback: Callable[[Message], Coroutine[Any, Any, Any]]
    ) -> None:
        """Unregisters a subscription for a message type.

        Parameters
        ----------
        message_type: type[:class:`Message`]
            The type of message to unsubscribe from.
        callback: Callable[[:class:`Message`],
            The callback to remove from the subscription.
        """
        self._callbacks[message_type].remove(callback)
        if not self._callbacks[message_type]:
            del self._callbacks[message_type]
