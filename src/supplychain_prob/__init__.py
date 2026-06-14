from __future__ import annotations
import builtins
from .ranvar import Ranvar, ranvar, dirac, poisson, negativeBinomial, transform
from .ranvar import uniform_rv as _uniform_rv
from .zedfunc import Zedfunc, constant, linear, uniform, valueAt
from . import pricebrk, extend, loglikelihood
from .metrics import crps, fillrate
from .fit import fit_zinb, ZINBFit
from .montecarlo import montecarlo, avg, ranvar_acc, SimulationContext, SimulationStepResult, MonteCarloResult

def quantile(r: Ranvar, p: float) -> int:
    return r.quantile(p)

def cdf(r: Ranvar) -> Zedfunc:
    return r.cdf()

def integral(obj, low: int, high: int) -> float:
    return obj.integral(low, high)

int = integral

def mixture(*args, weights=None):
    from .ranvar import from_items, dirac
    if len(args)==1 and not isinstance(args[0], Ranvar):
        rvs=list(args[0]); ws=[1.0]*len(rvs) if weights is None else list(weights)
    elif len(args) in (3,5,7):
        rvs=list(args[0::2]); ps=list(args[1::2]); ws=ps+[1-sum(ps)]
    else:
        raise TypeError('invalid mixture arguments')
    if not rvs: return dirac(0)
    if len(rvs)!=len(ws): raise ValueError('weights length mismatch')
    if any(w < 0 for w in ws) or sum(ws)<=0: raise ValueError('invalid mixture weights')
    total=sum(ws); out={}
    for rv,w in zip(rvs,ws):
        for l,h,m in zip(rv.lows,rv.highs,rv.masses): out[(builtins.int(l),builtins.int(h))]=out.get((builtins.int(l),builtins.int(h)),0.0)+float(m)*w/total
    return from_items(out)

def truncate(d: Ranvar, low: int, high: int) -> Ranvar:
    from ._validation import require_integer
    from .ranvar import buckets, dirac
    low=require_integer(low,'low'); high=require_integer(high,'high')
    if low>high: raise ValueError(f'truncate(_, {low}, {high}): expected {low} smaller or equal to {high}.')
    if low>d.support_max(): return dirac(low)
    if high<d.support_min(): return dirac(high)
    rows=[]
    for l,h,m in zip(d.lows,d.highs,d.masses):
        ovl=max(low,builtins.int(l)); ovh=min(high,builtins.int(h))
        if ovl<=ovh: rows.append((float(m)*(ovh-ovl+1)/(builtins.int(h)-builtins.int(l)+1),ovl,ovh))
    return buckets([x[0] for x in rows],[x[1] for x in rows],[x[2] for x in rows])

__all__ = ['Ranvar','Zedfunc','ranvar','dirac','poisson','negativeBinomial','quantile','cdf','int','integral','transform','mixture','truncate','crps','fillrate','valueAt','constant','linear','uniform','pricebrk','extend','loglikelihood','fit_zinb','montecarlo','avg','ranvar_acc','SimulationContext','SimulationStepResult','MonteCarloResult']
