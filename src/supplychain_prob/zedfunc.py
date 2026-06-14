from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
import numpy as np, pandas as pd
from ._validation import require_integer, require_finite_number

@dataclass(frozen=True)
class Zedfunc:
    func: Callable[[int], float]
    def value_at(self,k:int)->float: return float(self.func(require_integer(k,'k')))
    def integral(self,low:int,high:int)->float:
        low=require_integer(low,'low'); high=require_integer(high,'high')
        if low>high: raise ValueError('low must be <= high.')
        return float(sum(self.value_at(i) for i in range(low,high+1)))
    def to_dataframe(self, low:int, high:int)->pd.DataFrame:
        return pd.DataFrame({'Index':range(low,high+1),'Value':[self.value_at(i) for i in range(low,high+1)]})
    def plot(self, low:int, high:int, ax=None):
        import matplotlib.pyplot as plt
        ax=ax or plt.gca(); df=self.to_dataframe(low,high); ax.step(df['Index'],df['Value'],where='mid'); return ax
    def _op(self,o:Any,f):
        if isinstance(o,Zedfunc): return Zedfunc(lambda k:f(self.value_at(k),o.value_at(k)))
        c=require_finite_number(o,'constant'); return Zedfunc(lambda k:f(self.value_at(k),c))
    def __add__(self,o): return self._op(o,lambda a,b:a+b)
    def __sub__(self,o): return self._op(o,lambda a,b:a-b)
    def __mul__(self,o): return self._op(o,lambda a,b:a*b)

def constant(x:float)->Zedfunc:
    v=require_finite_number(x,'x'); return Zedfunc(lambda k:v)
def linear(a:float)->Zedfunc:
    v=require_finite_number(a,'a'); return Zedfunc(lambda k:v*k)
def valueAt(z:Zedfunc,k:int)->float: return z.value_at(k)
def integral(z:Zedfunc,low:int,high:int)->float: return z.integral(low,high)
class UniformNamespace:
    def left(self,n:int)->Zedfunc:
        n=require_integer(n,'n',context="'uniform.left(n)' is rounding fractional numbers")
        return Zedfunc(lambda k: 1.0 if 0 <= k <= n else 0.0)
uniform=UniformNamespace()
