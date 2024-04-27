from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar

if TYPE_CHECKING:
    from .model import Message, RequestType


T_MSG = TypeVar("T_MSG", bound="Message")
T_REQ = TypeVar("T_REQ", "Literal[RequestType.single]", "Literal[RequestType.multi]")
