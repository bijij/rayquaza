from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeVar

if TYPE_CHECKING:
    from .model import Message, Request, RequestType


T = TypeVar("T")

__all__ = (
    "MessagePublishedException",
    "UnqualifiedRequestTypeException",
    "BadResponseError",
    "NoActiveSubscribersException",
)


class MessagePublishedException(RuntimeError):
    """Raised when a message has already been published.

    Arributes
    ---------
    message : :class:`Message`
        The message that has already been published.
    """

    def __init__(self, message: Message) -> None:
        self.message: Message = message
        super().__init__(f"Message {message} has already been published")


class UnqualifiedRequestTypeException(TypeError):
    """Raised when the request type is unqualified.

    Attributes
    ----------
    request : :class:`Request`
        The request that has an unqualified request type.
    """

    def __init__(self, request: Request[Any, Any]) -> None:
        self.request: Request[Any, Any] = request
        super().__init__(f"Request type for request {request} is unqualified")


class BadResponseError(TypeError):
    """Raised when the response type does not match the expected response type.

    Attributes
    ----------
    request : :class:`Request`
        The request that was made.
    response : ``Any``
        The response that was received.
    expected : Type[``Any``]
        The expected response type.
    """

    def __init__(self, request: Request[T, Any], response: Any, expected: type[T]) -> None:
        self.request: Request[Any, Any] = request
        self.response: Any = response
        self.expected: type[Any] = expected
        super().__init__(f"Response {response} does not match expected type {expected}")


class NoActiveSubscribersException(RuntimeError):
    """Raised when there are no active subscriptions for the request type.

    Attributes
    ----------
    request : :class:`Request`
        The request that has no active subscriptions.
    """

    def __init__(self, request: Request[Any, Literal[RequestType.single]]) -> None:
        self.request: Request[Any, Literal[RequestType.single]] = request
        super().__init__(f"Request of type {request} has no active subscriptions.")
