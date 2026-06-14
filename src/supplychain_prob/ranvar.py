from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable
import numpy as np, pandas as pd
from scipy import stats
from ._validation import require_domain, require_integer, require_non_negative_weight, require_probability, MIN_RANVAR_VALUE, MAX_RANVAR_VALUE
from .buckets import CANONICAL_BUCKETS, accumulate_uniform_segment, bucket_for_value, overlapping_buckets

MAX_EXACT_POINTS=200_000

def _norm(items: dict[tuple[int,int], float]) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    s=sum(items.values())
    if s<=0: items={bucket_for_value(0):1.0}; s=1
    pairs=sorted((k,v/s) for k,v in items.items() if v>0)
    return (np.array([p[0][0] for p in pairs], dtype=np.int64), np.array([p[0][1] for p in pairs], dtype=np.int64), np.array([p[1] for p in pairs], dtype=np.float32))

@dataclass(frozen=True)
class Ranvar:
    lows: np.ndarray; highs: np.ndarray; masses: np.ndarray
    def __post_init__(self) -> None:
        object.__setattr__(self,'lows',np.asarray(self.lows,dtype=np.int64)); object.__setattr__(self,'highs',np.asarray(self.highs,dtype=np.int64)); object.__setattr__(self,'masses',np.asarray(self.masses,dtype=np.float32))
        if len(self.lows)==0 or not (len(self.lows)==len(self.highs)==len(self.masses)): raise ValueError('Invalid ranvar arrays.')
        require_domain(int(self.lows[0]), int(self.highs[-1]))
        if np.any(self.lows>self.highs) or np.any(self.masses<0) or not np.all(np.isfinite(self.masses)): raise ValueError('Invalid ranvar data.')
        if not np.isclose(float(np.sum(self.masses,dtype=np.float64)),1.0,atol=1e-5): raise ValueError('Ranvar mass must sum to 1.')
    def support_min(self)->int: return int(self.lows[0])
    def support_max(self)->int: return int(self.highs[-1])
    def mean(self)->float:
        return float(np.sum(((self.lows+self.highs)/2)*self.masses,dtype=np.float64))
    def variance(self)->float:
        means=(self.lows+self.highs)/2; widths=self.highs-self.lows+1
        ex2=((self.lows*self.lows + self.lows*self.highs + self.highs*self.highs)/3 + (widths*widths-1)/12)
        m=self.mean(); return float(np.sum(ex2*self.masses,dtype=np.float64)-m*m)
    def dispersion(self)->float: return self.variance()/self.mean() if self.mean()>0 else 0.0
    def integral(self, low:int, high:int)->float:
        low=require_integer(low,'low'); high=require_integer(high,'high')
        if low>high: raise ValueError(f'expected {low} smaller or equal to {high}.')
        total=0.0
        for l,h,m in zip(self.lows,self.highs,self.masses):
            ov=max(0,min(high,int(h))-max(low,int(l))+1)
            if ov: total += float(m)*ov/(int(h)-int(l)+1)
        return float(total)
    def cdf_at(self,k:int)->float: k=require_integer(k,'k'); return self.integral(MIN_RANVAR_VALUE,k)
    def quantile(self,p:float)->int:
        p=require_probability(p,'p'); acc=0.0
        for l,h,m in zip(self.lows,self.highs,self.masses):
            if acc+float(m) >= p-1e-15:
                if m==0: return int(l)
                frac=max(0.0,(p-acc)/float(m)); width=int(h)-int(l)+1
                return int(l)+min(width-1, max(0, int(np.ceil(frac*width)-1)))
            acc += float(m)
        return self.support_max()
    def cdf(self):
        from .zedfunc import Zedfunc
        return Zedfunc(lambda k:self.cdf_at(k))
    def sample(self,n:int,seed:int|None=None)->np.ndarray:
        n=require_integer(n,'n');
        if n<0: raise ValueError('n must be non-negative.')
        rng=np.random.default_rng(seed); idx=rng.choice(len(self.masses),size=n,p=self.masses.astype(float)/float(np.sum(self.masses,dtype=np.float64)))
        return np.array([rng.integers(int(self.lows[i]), int(self.highs[i])+1) for i in idx], dtype=np.int64)
    def to_dataframe(self, include_zero_buckets: bool=False)->pd.DataFrame:
        rows=[]
        source=zip(self.lows,self.highs,self.masses) if not include_zero_buckets else [(l,h,self.integral(l,h)) for l,h in CANONICAL_BUCKETS]
        c=0.0
        for l,h,m in source:
            if m==0 and not include_zero_buckets: continue
            w=int(h)-int(l)+1; cm=(int(l)+int(h))/2; lowc=c; c+=float(m)
            rows.append({'Min':int(l),'Max':int(h),'Mass':float(m),'Width':w,'Density':float(m)/w,'BucketMean':cm,'CdfLow':lowc,'CdfHigh':c})
        return pd.DataFrame(rows)
    def extend_ranvar(self, gap:int|None=None, multiplier:int|None=None, reach:int|None=None, *, include_mass:bool=True)->pd.DataFrame: return self.to_dataframe()
    def plot_pmf(self, ax=None, *, density: bool=True):
        import matplotlib.pyplot as plt
        ax=ax or plt.gca(); df=self.to_dataframe(); ax.bar(df['Min'], df['Density' if density else 'Mass'], width=df['Width'], align='edge'); return ax
    def plot_cdf(self, ax=None):
        import matplotlib.pyplot as plt
        ax=ax or plt.gca(); df=self.to_dataframe(); ax.step(df['Max'], df['CdfHigh'], where='post'); return ax
    def __add__(self,o:Any): return _binary(self,o,lambda a,b:a+b)
    def __sub__(self,o:Any): return _binary(self,o,lambda a,b:a-b)
    def __mul__(self,o:Any): return _binary(self,o,lambda a,b:a*b)
    def __pow__(self,o:Any):
        if isinstance(o,(int,np.integer)) and o>=0:
            r=dirac(0 if o==0 else 1)
            for _ in range(int(o)): r=r*self
            return r
        return transform(self,float(o))

def from_items(items: dict[tuple[int,int], float])->Ranvar:
    return Ranvar(*_norm(items))

def dirac(n:int)->Ranvar:
    n=require_integer(n,'n',context=f'dirac({n})'); require_domain(n,n); return from_items({bucket_for_value(n):1.0})

def ranvar_values(values: Iterable[Any], weights: Iterable[Any]|None=None)->Ranvar:
    vals=list(values); ws=[1.0]*len(vals) if weights is None else [require_non_negative_weight(w,'weight') for w in weights]
    if len(vals)!=len(ws): raise ValueError('values and weights must have same length.')
    out={}
    for v,w in zip(vals,ws):
        iv=require_integer(v,'value'); require_domain(iv,iv); out[bucket_for_value(iv)]=out.get(bucket_for_value(iv),0.0)+w
    return from_items(out) if sum(ws)>0 else dirac(0)

def buckets(weight, low, high)->Ranvar:
    def arr(x): return list(x) if isinstance(x,(list,tuple,np.ndarray,pd.Series)) else [x]
    ws,ls,hs=arr(weight),arr(low),arr(high)
    if not(len(ws)==len(ls)==len(hs)): raise ValueError('bucket inputs must have same length.')
    seg=[]; out={}
    for w,l,h in zip(ws,ls,hs):
        ww=require_non_negative_weight(w,'weight'); ll=require_integer(l,'low'); hh=require_integer(h,'high'); require_domain(ll,hh)
        if any(not(hh < a or ll > b) for a,b in seg): raise ValueError('input buckets must not overlap.')
        seg.append((ll,hh)); accumulate_uniform_segment(ll,hh,ww,out)
    return from_items(out) if sum(float(x) for x in ws)>0 else dirac(0)

def uniform_rv(*args:Any)->Ranvar:
    if len(args)==1: low,high=0,args[0]
    elif len(args)==2: low,high=args
    else: raise TypeError('uniform expects one or two bounds.')
    low=require_integer(low,'low'); high=require_integer(high,'high'); return buckets([1.0],[low],[high])

def _binary(a:Ranvar,b:Any,op):
    if not isinstance(b,Ranvar): b=dirac(b)
    out={}
    for l1,h1,m1 in zip(a.lows,a.highs,a.masses):
      for l2,h2,m2 in zip(b.lows,b.highs,b.masses):
        vals=[op(int(l1),int(l2)),op(int(l1),int(h2)),op(int(h1),int(l2)),op(int(h1),int(h2))]
        accumulate_uniform_segment(min(vals),max(vals),float(m1)*float(m2),out)
    return from_items(out)

def transform(r:Ranvar,a:float)->Ranvar:
    from ._rounding import bankers_round_to_int
    a=np.float32(a); out={}
    for l,h,m in zip(r.lows,r.highs,r.masses):
        lo=int(bankers_round_to_int(float(l)*float(a))); hi=int(bankers_round_to_int(float(h)*float(a)))
        if lo>hi: lo,hi=hi,lo
        accumulate_uniform_segment(lo,hi,float(m),out)
    return from_items(out)

class RanvarNamespace:
    def __call__(self, values, weights=None): return ranvar_values(values,weights)
    def buckets(self, weight, low, high): return buckets(weight,low,high)
    def uniform(self,*args): return uniform_rv(*args)
    def groupby(self, values, groups, weights=None):
        d={}
        for g in set(groups):
            idx=[i for i,x in enumerate(groups) if x==g]; d[g]=ranvar_values([list(values)[i] for i in idx], None if weights is None else [list(weights)[i] for i in idx])
        return d
    def aggregate(self, df:pd.DataFrame, value_col:str, by, weight_col:str|None=None):
        rows=[]
        for key,grp in df.groupby(by):
            rv=ranvar_values(grp[value_col], None if weight_col is None else grp[weight_col])
            vals=key if isinstance(key,tuple) else (key,); cols=by if isinstance(by,list) else [by]
            rows.append({**dict(zip(cols,vals)), 'Ranvar':rv})
        return pd.DataFrame(rows)
ranvar=RanvarNamespace()

def poisson(mean:float)->Ranvar:
    if not np.isfinite(mean) or mean<0 or mean>1_000_000: raise ValueError('mean must be in range.')
    hi=max(0,int(stats.poisson.ppf(1-2e-5,mean))); xs=np.arange(0,hi+1); ps=stats.poisson.pmf(xs,mean); return ranvar_values(xs,ps)

def negativeBinomial(mean:float, dispersion:float, zeroInflation:float=0.0)->Ranvar:
    if mean<=0 or dispersion<1 or not np.isfinite(mean+dispersion): raise ValueError('invalid parameters.')
    zi=max(0,min(float(zeroInflation),0.999)); hi=max(0,int(mean+10*np.sqrt(mean*dispersion)+20)); xs=np.arange(0,hi+1)
    if dispersion>=1.001:
        r=mean/(dispersion-1); p=1/dispersion; ps=stats.nbinom.pmf(xs,r,p)
    else: ps=stats.poisson.pmf(xs,mean)
    ps=ps*(1-zi); ps[0]+=zi; return ranvar_values(xs,ps)
