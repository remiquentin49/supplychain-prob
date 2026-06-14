from __future__ import annotations
from .zedfunc import Zedfunc
from ._validation import require_integer, require_finite_number

def _validate(base, breaks, prices):
    base=require_finite_number(base,'base'); bs=[require_integer(b,'break') for b in breaks]; ps=[require_finite_number(p,'price') for p in prices]
    if len(bs)!=len(ps): raise ValueError('breaks and prices length mismatch.')
    if any(b<=0 for b in bs) or any(bs[i]>=bs[i+1] for i in range(len(bs)-1)): raise ValueError('breaks must be increasing.')
    return base,bs,ps

def f(base, breaks, prices):
    base,bs,ps=_validate(base,breaks,prices)
    def val(k:int):
        price=base
        for b,p in zip(bs,ps):
            if k>=b: price=p
        return price
    return Zedfunc(val)

def m(base, breaks, prices):
    base,bs,ps=_validate(base,breaks,prices)
    def unit(q:int):
        price=base
        for b,p in zip(bs,ps):
            if q>=b: price=p
        return price
    return Zedfunc(lambda k: k*unit(k)-(k-1)*unit(k-1) if k>0 else 0.0)
