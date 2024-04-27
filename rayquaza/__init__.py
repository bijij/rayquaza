"""
Rayquaza: An asynchronous python mediator.

"""

from __future__ import annotations

from typing import NamedTuple

from .core import *
from .core import __all__ as _core_all
from .exception import *
from .exception import __all__ as _exception_all
from .model import *
from .model import __all__ as _model_all


class _VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release: str
    serial: int


version: str = "0.1.0a"
version_info: _VersionInfo = _VersionInfo(0, 1, 0, "alpha", 0)

__all__ = [
    *_exception_all,
    *_core_all,
    *_model_all,
    "version",
    "version_info",
]
