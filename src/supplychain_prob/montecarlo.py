from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence
import numpy as np, pandas as pd
from ._validation import require_integer, require_finite_number
from .ranvar import Ranvar, ranvar_values
@dataclass(frozen=True)
class SimulationContext: simulation_id:int; rng:np.random.Generator; debug:bool
@dataclass(frozen=True)
class SimulationStepResult: values:Mapping[str,Any]; debug_rows:Sequence[Mapping[str,Any]]=()
@dataclass(frozen=True)
class MonteCarloResult: values:Mapping[str,Any]; debug:pd.DataFrame|None; iterations:int; seed:int|None
class AvgAccumulator:
    def __init__(self, field, output=None): self.field=field; self.output=output or field; self.s=0.0; self.n=0
    def add(self,v): self.s+=require_finite_number(v,self.field); self.n+=1
    def result(self): return self.s/self.n
class RanvarAccumulator:
    def __init__(self, field, output=None): self.field=field; self.output=output or field; self.val=[]
    def add(self,v): self.val.append(require_integer(v,self.field))
    def result(self)->Ranvar: return ranvar_values(self.val)
def avg(field, *, output=None): return AvgAccumulator(field,output)
def ranvar_acc(field, *, output=None): return RanvarAccumulator(field,output)
def montecarlo(iterations:int, seed:int|None, step:Callable[[SimulationContext],Mapping[str,Any]|SimulationStepResult], accumulators:Sequence[Any], *, debug_simulation_id:int|None=None)->MonteCarloResult:
    iterations=require_integer(iterations,'iterations')
    if iterations<=0: raise ValueError('iterations must be positive.')
    if debug_simulation_id is not None and not (0 <= debug_simulation_id < iterations): raise ValueError('invalid debug id.')
    dbg=[]
    for i in range(iterations):
        ctx=SimulationContext(i,np.random.default_rng(np.random.SeedSequence([seed if seed is not None else np.random.SeedSequence().entropy,i])),i==debug_simulation_id)
        out=step(ctx); vals=out.values if isinstance(out,SimulationStepResult) else out
        for acc in accumulators: acc.add(vals[acc.field])
        if isinstance(out,SimulationStepResult) and ctx.debug: dbg.extend(out.debug_rows)
    return MonteCarloResult({a.output:a.result() for a in accumulators}, pd.DataFrame(dbg) if debug_simulation_id is not None else None, iterations, seed)
