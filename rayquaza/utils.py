from __future__ import annotations

from typing import Any


class _MissingSentinel:
    def __repr__(self) -> str:
        return "..."

    def __bool__(self) -> bool:
        return False


MISSING: Any = _MissingSentinel()
