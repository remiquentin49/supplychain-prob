from __future__ import annotations
import numpy as np
from .ranvar import Ranvar, dirac, ranvar_values
from ._validation import require_integer

def fillrate(r:Ranvar)->Ranvar:
    vals=[]; probs=[]
    for l,h,m in zip(r.lows,r.highs,r.masses):
        for k in range(max(1,int(l)), int(h)+1): vals.append(k); probs.append(float(m)/(int(h)-int(l)+1))
    mean=sum(v*p for v,p in zip(vals,probs))
    if mean<=0: return dirac(0)
    ks=sorted(set(vals)); masses=[sum(p for v,p in zip(vals,probs) if v>=k)/mean for k in ks]
    return ranvar_values(ks,masses)

def crps(r, obs)->float:
    if isinstance(obs,Ranvar):
        lo=min(r.support_min(),obs.support_min()); hi=max(r.support_max(),obs.support_max())
        return float(sum((r.cdf_at(k)-obs.cdf_at(k))**2 for k in range(lo,hi+1)))
    n=require_integer(obs,'n'); return float(sum((r.cdf_at(k)-(0 if k<n else 1))**2 for k in range(r.support_min(),r.support_max()+1)))
