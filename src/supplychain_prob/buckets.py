from __future__ import annotations
import bisect
from ._validation import MAX_RANVAR_VALUE, MIN_RANVAR_VALUE, require_domain

_POS: list[tuple[int,int]] = [(i,i) for i in range(65)]
for j in range(1,20):
    w = 2**j; start = 128*(2**(j-1))-63
    for i in range(64):
        _POS.append((start+i*w, start+(i+1)*w-1))
NEGATIVE_BUCKETS = [(-h,-l) for l,h in _POS if l>0]
NEGATIVE_BUCKETS.reverse()
POSITIVE_BUCKETS = _POS
CANONICAL_BUCKETS = tuple(NEGATIVE_BUCKETS + POSITIVE_BUCKETS)
LOWS = [x[0] for x in CANONICAL_BUCKETS]
HIGHS = [x[1] for x in CANONICAL_BUCKETS]

def bucket_for_value(v: int) -> tuple[int,int]:
    require_domain(v,v)
    i = bisect.bisect_right(LOWS, v) - 1
    b = CANONICAL_BUCKETS[i]
    if not (b[0] <= v <= b[1]): raise ValueError(f"No bucket for {v}.")
    return b

def overlapping_buckets(low: int, high: int) -> list[tuple[int,int]]:
    require_domain(low, high)
    i = max(0, bisect.bisect_right(HIGHS, low-1))
    out=[]
    while i < len(CANONICAL_BUCKETS) and LOWS[i] <= high:
        out.append(CANONICAL_BUCKETS[i]); i += 1
    return out

def accumulate_uniform_segment(low: int, high: int, weight: float, out: dict[tuple[int,int], float]) -> None:
    require_domain(low, high)
    width = high-low+1
    for bl,bh in overlapping_buckets(low, high):
        ov = max(0, min(high,bh)-max(low,bl)+1)
        if ov: out[(bl,bh)] = out.get((bl,bh),0.0) + weight*ov/width
