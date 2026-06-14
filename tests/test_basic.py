from pathlib import Path
import pytest
import numpy as np
from supplychain_prob import *
from supplychain_prob.buckets import CANONICAL_BUCKETS, bucket_for_value

def test_grid_and_basic():
    assert len(CANONICAL_BUCKETS)==2561
    assert CANONICAL_BUCKETS[0][0] == -67108800
    assert CANONICAL_BUCKETS[-1][1] == 67108800
    assert bucket_for_value(1000)==(993,1008)
    assert bucket_for_value(-1000)==(-1008,-993)
    r=dirac(100)
    assert r.support_min()==99 and r.support_max()==100
    assert int(r,99,99)==pytest.approx(.5)
    assert r.mean()==pytest.approx(99.5)

def test_constructors_ops():
    assert ranvar([1,2], weights=[1,2]).mean()==pytest.approx(5/3)
    assert ranvar.buckets([.4,.6],[0,2],[1,3]).mean()==pytest.approx(1.7)
    assert ranvar.uniform(5,10).mean()==pytest.approx(7.5)
    assert quantile(poisson(3), .9) >= 4
    assert transform(dirac(1),2.5).mean()==pytest.approx(2)
    assert truncate(ranvar.uniform(1,6),2,4).mean()==pytest.approx(3)
    assert mixture(poisson(1),.25,poisson(3)).mean()==pytest.approx(2.5, abs=.1)

def test_zed_price_metrics():
    assert valueAt(linear(2),3)==6
    z=pricebrk.m(10,[5,10],[9,8])
    assert [valueAt(z,k) for k in range(1,13)] == [10,10,10,10,5,9,9,9,9,-1,8,8]
    assert int(z,1,10)==80
    f=fillrate(poisson(2)); assert int(f, f.support_min(), f.support_max())==pytest.approx(1, abs=1e-5)
    assert crps(poisson(3),4)==pytest.approx(.68, abs=.1)

def test_loglik_fit_mc_plot():
    assert loglikelihood.negativeBinomial(2,1.5,3)==pytest.approx(-1.921965, abs=1e-6)
    assert loglikelihood.negativeBinomial(2,1.5,.2,0)==pytest.approx(-1.027153, abs=1e-6)
    fit=fit_zinb([0,1,2,0,3], starts=2, seed=1); assert fit.converged or fit.mean>0
    def step(ctx):
        d=ctx.rng.poisson(3)
        return SimulationStepResult({'demand':d,'reward':2*d}, [{'SimulationId':ctx.simulation_id}] if ctx.debug else [])
    res=montecarlo(20,42,step,[avg('reward'),ranvar_acc('demand')],debug_simulation_id=2)
    assert 'reward' in res.values and res.debug is not None
    assert poisson(2).to_dataframe()['Mass'].sum()==pytest.approx(1)
    assert poisson(2).plot_pmf() is not None

def test_invalid_and_scan():
    with pytest.raises(ValueError): dirac(.8)
    with pytest.raises(ValueError): ranvar([1, np.nan])
    forbidden=["Lo"+"kad","lo"+"kad","En"+"vision","en"+"vision","docs."+"lo"+"kad","en"+"vision."+"lo"+"kad"]
    suffixes={'.py','.md','.toml','.txt','.yml','.yaml'}
    ignored={'.git','.venv','__pycache__','.pytest_cache','.ruff_cache','.mypy_cache','dist','build'}
    for path in Path('.').rglob('*'):
        if any(part in ignored or part.endswith('.egg-info') for part in path.parts) or path.suffix not in suffixes or not path.is_file():
            continue
        text=path.read_text(errors='ignore')
        for token in forbidden:
            assert token not in text, f'{path} contains {token}'
