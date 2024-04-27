from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, TypeVar, get_args, get_origin

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

from .types import T_REQ

T = TypeVar("T")

__all__ = (
    "Message",
    "Request",
    "RequestType",
    "SingleResponseRequest",
    "MultiResponseRequest",
)


class RequestType(Enum):
    """
    The type of request to be made.
    """

    single = auto()
    """A request that expects a single response."""

    multi = auto()
    """A request that expects multiple responses."""


class _ModelBase:
    pass


class Message(_ModelBase):
    """The base class for all mediator messages."""

    __mediator_published__: bool = False


class Request(Message, Generic[T, T_REQ]):
    """The base class for all mediator requests.

    .. tip::
        Use :class:`SingleResponseRequest` or :class:`MultiResponseRequest`
        to create a request that expects a single or multiple responses respectively.
    """

    __mediator_request_type__: ClassVar[RequestType]
    __mediator_response_type__: ClassVar[type[Any]]

    def __init_subclass__(cls) -> None:
        for orig_base in getattr(cls, "__orig_bases__", ()):
            if get_origin(orig_base) is Request:
                response_type, request_type = get_args(orig_base)
                cls.__mediator_response_type__ = response_type
                cls.__mediator_request_type__ = get_args(request_type)[0]
                break


SingleResponseRequest: TypeAlias = Request[T, Literal[RequestType.single]]

MultiResponseRequest: TypeAlias = Request[T, Literal[RequestType.multi]]
