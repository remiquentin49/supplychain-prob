from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
from ._validation import require_integer, require_non_negative_weight
from .ranvar import negativeBinomial, Ranvar
from . import loglikelihood
@dataclass(frozen=True)
class ZINBFit:
    mean: float; dispersion: float; zeroInflation: float; loglikelihood: float; converged: bool; optimizer_message: str; n_obs: int; n_eff: float
    def to_ranvar(self)->Ranvar: return negativeBinomial(self.mean,self.dispersion,self.zeroInflation)
def _sig(x): return 1/(1+np.exp(-x))
def _soft(x): return np.log1p(np.exp(-abs(x)))+np.maximum(x,0)
def fit_zinb(counts, weights=None, *, starts:int=20, seed:int|None=0, method:str='L-BFGS-B')->ZINBFit:
    xs=np.array([require_integer(x,'count') for x in counts],dtype=int)
    if len(xs)==0 or np.any(xs<0): raise ValueError('counts must be non-empty non-negative integers.')
    ws=np.ones(len(xs)) if weights is None else np.array([require_non_negative_weight(w,'weight') for w in weights],float)
    if len(ws)!=len(xs) or ws.sum()<=0: raise ValueError('invalid weights.')
    starts=require_integer(starts,'starts');
    if starts<=0: raise ValueError('starts must be positive.')
    m=float(np.average(xs,weights=ws)); var=float(np.average((xs-m)**2,weights=ws)); disp=max(var/m if m>0 else 1.001,1.001); zero=max(0,min(float(np.mean(xs==0)-np.exp(-max(m,1e-6))),0.5))
    def inv_soft(y): return np.log(np.expm1(max(y,1e-6)))
    base=np.array([inv_soft(m), inv_soft(disp-1), np.log(max(zero/0.999,1e-6)/(1-max(zero/0.999,1e-6)))])
    rng=np.random.default_rng(seed); best=None
    def unpack(t): return float(_soft(t[0])+1e-9), float(1+_soft(t[1])), float(0.999*_sig(t[2]))
    def obj(t):
        mm,dd,zz=unpack(t); return -sum(w*loglikelihood.negativeBinomial(mm,dd,zz,int(x)) for x,w in zip(xs,ws))
    for i in range(starts):
        res=minimize(obj, base+(rng.normal(0,0.5,3) if i else 0), method=method)
        if best is None or res.fun < best.fun: best=res
    mm,dd,zz=unpack(best.x); ll=-float(best.fun)
    return ZINBFit(mm,dd,zz,ll,bool(best.success),str(best.message),len(xs),float(ws.sum()))
