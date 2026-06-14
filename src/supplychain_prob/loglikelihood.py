from __future__ import annotations
import math
from scipy.special import gammaln
from ._validation import clamp_zero_inflation, require_integer

def negativeBinomial(mean, dispersion, *args):
    if len(args)==1: alpha=0.0; k=args[0]
    elif len(args)==2: alpha=clamp_zero_inflation(args[0]); k=args[1]
    else: raise TypeError('expected k or zeroInflation, k')
    mean=float(mean); dispersion=float(dispersion); k=require_integer(k,'k')
    if mean<=0 or dispersion<1 or k<0 or not math.isfinite(mean+dispersion): raise ValueError('invalid parameters.')
    if dispersion>=1.001:
        r=mean/(dispersion-1); p=1-1/dispersion
        if k==0 and alpha>0: return float(math.log(alpha+(1-alpha)*(1-p)**r))
        y=gammaln(k+r)-gammaln(k+1)-gammaln(r)+k*math.log(p)+r*math.log(1-p)
    else:
        if k==0 and alpha>0: return float(math.log(alpha+(1-alpha)*math.exp(-mean)))
        y=k*math.log(mean)-mean-gammaln(k+1)
    return float(y + (math.log(1-alpha) if alpha>0 and k>0 else 0.0))
