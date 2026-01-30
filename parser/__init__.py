from typing import Any

from .model import Weight, Set_, Exercise, Units
from .standardize_name import StandardizeName

# Lazy import to avoid ANTLR dependency
def __getattr__(name: str) -> Any:
    if name == "Formatter" or name == "Parser":
        from .parser import Formatter, Parser
        return Formatter if name == "Formatter" else Parser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "Weight",
    "Set_",
    "Exercise",
    "Units",
    "StandardizeName",
    "Formatter",
    "Parser",
]
