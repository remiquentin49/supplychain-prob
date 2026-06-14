# supplychain_prob

This package is provided for educational purpose only and must not be used for commercial usage.

`supplychain_prob` is a small, deterministic, in-memory Python package for probabilistic models over integer supply quantities. It focuses on inspectable compressed random variables, integer validation, simple cost functions, fitting, metrics, plotting, and reproducible Monte Carlo accumulation.

## Installation

```bash
python -m pip install -e ".[dev]"
```

## Quickstart

```python
from supplychain_prob import poisson, quantile, int

demand = poisson(3)

print(demand.mean())
print(quantile(demand, 0.9))
print(int(demand, 0, 2))
```

## Main concepts

A `Ranvar` is a compressed probability distribution over integer values. A `Zedfunc` is an integer-indexed function useful for marginal costs or rewards. Public arrays use compact dtypes, while fragile calculations use wider temporary precision.

The package is strict about integer quantities: support values, observations, bucket bounds, and evaluation indices must be integer-valued and finite. Fractional quantities are rejected instead of rounded.

## Examples

```python
from supplychain_prob import ranvar

r = ranvar.buckets(
    weight=[0.4, 0.6],
    low=[0, 2],
    high=[1, 3],
)

print(r.mean())  # around 1.7
```

```python
from supplychain_prob import pricebrk, valueAt, int

z = pricebrk.m(10, [5, 10], [9, 8])

print(valueAt(z, 5))      # 5
print(valueAt(z, 10))     # -1
print(int(z, 1, 10))      # 80
```

```python
from supplychain_prob import montecarlo, avg, ranvar_acc, SimulationStepResult

def step(ctx):
    demand = ctx.rng.poisson(3)
    return SimulationStepResult(
        values={"demand": demand, "reward": 2.0 * demand},
        debug_rows=[{"SimulationId": ctx.simulation_id, "Demand": demand}] if ctx.debug else [],
    )

result = montecarlo(
    iterations=1000,
    seed=42,
    step=step,
    accumulators=[avg("reward"), ranvar_acc("demand")],
    debug_simulation_id=3,
)

print(result.values["reward"])
print(result.values["demand"].mean())
print(result.debug)
```

## Testing

```bash
pytest -q
ruff check .
mypy src
```

## Known design notes

The model is in-memory only and has no ranvar serialization format. Wide tails are represented by canonical integer buckets, and mass inside each bucket is interpreted uniformly. The package avoids allocating the full integer domain.
