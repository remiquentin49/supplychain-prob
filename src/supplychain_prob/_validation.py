from __future__ import annotations
import math
from collections.abc import Sequence
from ._errors import DomainError, FractionalValueError, ValidationError
MIN_RANVAR_VALUE = -67_108_800
MAX_RANVAR_VALUE = 67_108_800

def require_finite_number(x: object, name: str) -> float:
    try: v = float(x)  # type: ignore[arg-type]
    except Exception as exc: raise ValidationError(f"{name} must be a finite number.") from exc
    if not math.isfinite(v): raise ValidationError(f"{name} must be finite.")
    return v

def require_integer(x: object, name: str, *, context: str | None = None) -> int:
    v = require_finite_number(x, name)
    if not v.is_integer():
        msg = f"{context}: fractional arguments are not supported." if context else f"{name} must be integer-valued."
        raise FractionalValueError(msg)
    return int(v)

def require_probability(x: object, name: str) -> float:
    v = require_finite_number(x, name)
    if v < 0 or v > 1: raise ValidationError(f"{name} must be between 0 and 1.")
    return v

def require_non_negative_weight(x: object, name: str) -> float:
    v = require_finite_number(x, name)
    if v < 0: raise ValidationError(f"{name} must be non-negative.")
    return v

def clamp_zero_inflation(x: object, name: str = "zeroInflation") -> float:
    return min(max(require_finite_number(x, name), 0.0), 0.999)

def require_domain(low: int, high: int) -> None:
    if low < MIN_RANVAR_VALUE or high > MAX_RANVAR_VALUE or low > high:
        raise DomainError(f"Cannot create ranvar with domain [{low} .. {high}].")

def ensure_same_length(*arrays: Sequence[object], names: Sequence[str]) -> None:
    sizes = [len(a) for a in arrays]
    if len(set(sizes)) != 1: raise ValidationError(f"Expected same lengths for {', '.join(names)}.")
