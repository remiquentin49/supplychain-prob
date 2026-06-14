# Codex implementation prompt: build the complete Python package

You are Codex. Build a complete, installable, tested Python package from scratch.

This package is a small supply-chain probabilistic modelling library. It must implement the business-facing behavior described here. Do not stop at a plan. Create the package files, implement the code, write tests, run the tests, fix failures, and leave the repository in a clean working state.

The final package must be deterministic, strict about integer quantities, fully in-memory, easy to inspect, easy to debug, and reasonably performant without premature optimization.

---

## 0. Critical repository constraints

### 0.1 Forbidden references

Do not include any company or product references in:

- package name
- module names
- class names, unless explicitly required below
- function names, unless explicitly required below
- comments
- docstrings
- tests
- README
- examples
- changelog
- license
- pyproject metadata
- issue templates
- any generated file

The public API should keep compatibility-facing mathematical names such as:

```python
ranvar
zedfunc
dirac
poisson
negativeBinomial
quantile
cdf
int
integral
transform
mixture
truncate
crps
fillrate
pricebrk.f
pricebrk.m
constant
linear
uniform.left
valueAt
extend.ranvar
loglikelihood.negativeBinomial
```

These names are allowed because they are API/math names, not company/product names.

The repository must not contain these forbidden strings contiguously anywhere. In tests, construct them dynamically so the test file itself does not contain them contiguously:

```python
forbidden = [
    "Lo" + "kad",
    "lo" + "kad",
    "En" + "vision",
    "en" + "vision",
    "docs." + "lo" + "kad",
    "en" + "vision." + "lo" + "kad",
]
```

Create a repository scan test that fails if any forbidden token appears contiguously in any tracked source/documentation file.

### 0.2 README and license

The README must state exactly:

```text
This package is provided for educational purpose only and must not be used for commercial usage.
```

Create a simple custom `LICENSE` file with the same non-commercial educational-use restriction. Do not claim the package is MIT, Apache, BSD, or any other permissive open-source license, because those conflict with the non-commercial restriction.

### 0.3 Design principle

Implement observable business behavior, not a giant runtime clone.

Required qualities:

- deterministic
- strict on invalid supply-chain quantities
- in-memory only
- no file serialization format for ranvars
- DataFrame export for inspection
- robust tests
- clear error messages
- no silent repair of invalid user input
- no huge memory allocation over the full integer domain

---

## 1. Package name and repository layout

Use this package name unless there is already a local naming conflict:

```text
supplychain_prob
```

Use a modern `src/` package layout.

Expected files:

```text
pyproject.toml
README.md
LICENSE
src/supplychain_prob/__init__.py
src/supplychain_prob/py.typed

src/supplychain_prob/_errors.py
src/supplychain_prob/_validation.py
src/supplychain_prob/_rounding.py
src/supplychain_prob/buckets.py
src/supplychain_prob/ranvar.py
src/supplychain_prob/distributions.py
src/supplychain_prob/zedfunc.py
src/supplychain_prob/pricebrk.py
src/supplychain_prob/metrics.py
src/supplychain_prob/loglikelihood.py
src/supplychain_prob/fit.py
src/supplychain_prob/montecarlo.py
src/supplychain_prob/plotting.py
src/supplychain_prob/extend.py


tests/test_forbidden_terms.py
tests/test_bucket_grid.py
tests/test_validation.py
tests/test_ranvar_construction.py
tests/test_ranvar_operations.py
tests/test_distributions.py
tests/test_zedfunc.py
tests/test_pricebrk.py
tests/test_metrics.py
tests/test_loglikelihood_fit.py
tests/test_montecarlo.py
tests/test_plotting.py
tests/test_readme_examples.py
```

Recommended dependencies:

```text
runtime:
  numpy
  scipy
  pandas
  matplotlib

dev:
  pytest
  hypothesis
  ruff
  mypy
```

Use Python `>=3.11`.

The package should be installable with:

```bash
python -m pip install -e ".[dev]"
```

The quality gate should pass with:

```bash
pytest -q
ruff check .
mypy src
```

No placeholder tests. Every test must assert real behavior.

---

## 2. Public API

Expose the following from `supplychain_prob.__init__`:

```python
from supplychain_prob import (
    Ranvar,
    Zedfunc,
    ranvar,
    dirac,
    poisson,
    negativeBinomial,
    quantile,
    cdf,
    int,
    integral,
    transform,
    mixture,
    truncate,
    crps,
    fillrate,
    valueAt,
    constant,
    linear,
    uniform,
    pricebrk,
    extend,
    loglikelihood,
    fit_zinb,
    montecarlo,
    avg,
    ranvar_acc,
    SimulationContext,
    SimulationStepResult,
    MonteCarloResult,
)
```

Required call syntax:

```python
ranvar([1, 2, 3])
ranvar([1, 2, 3], weights=[1.0, 2.0, 3.0])
ranvar.buckets(weight=[0.4, 0.6], low=[0, 2], high=[1, 3])
ranvar.uniform(10)
ranvar.uniform(5, 10)
ranvar.groupby(values, groups, weights=None)
ranvar.aggregate(df, value_col="Qty", by="Sku", weight_col=None)

dirac(10)
poisson(3)
negativeBinomial(2.0, 1.5)
negativeBinomial(2.0, 1.5, 0.2)

quantile(poisson(3), 0.9)
cdf(poisson(3))
integral(poisson(3), 0, 2)
int(poisson(3), 0, 2)
transform(poisson(3), 2.5)

extend.ranvar(poisson(3))

pricebrk.f(10, [5, 10], [9, 8])
pricebrk.m(10, [5, 10], [9, 8])

constant(3.0)
linear(2.0)
uniform.left(0)
valueAt(linear(2.0), 3)

loglikelihood.negativeBinomial(2.0, 1.5, 3)
loglikelihood.negativeBinomial(2.0, 1.5, 0.2, 3)

fit_zinb([0, 1, 2, 0, 3])

montecarlo(...)
avg("reward")
ranvar_acc("demand")
```

Python naming caveat:

- Export a compatibility-facing function named `int`.
- Internally, do not accidentally shadow Python's built-in `int`.
- Implement the real function as `integral(...)`.
- Then expose `int = integral`.
- When the built-in integer constructor is required internally, use `builtins.int`.

Namespace implementation guidance:

- `ranvar` can be a callable namespace object with `__call__`, `.buckets`, `.uniform`, `.groupby`, `.aggregate`.
- `pricebrk` can be a namespace object or module with `.f` and `.m`.
- `uniform` can be a namespace object with `.left`.
- `extend` can be a namespace object or module with `.ranvar`.
- `loglikelihood` can be a namespace object or module with `.negativeBinomial`.

---

## 3. Numeric policy

This package is for supply-chain optimization, not high-precision scientific mathematics.

Use this policy consistently:

```text
storage/public dtype:
  float32 for masses, probabilities, zedfunc values, and public arrays

internal fragile calculations:
  float64 for cumulative sums, normalization, convolutions, log-likelihoods,
  optimizer objectives, scipy calls, and temporary probability calculations

integer quantities:
  int64 internally
```

At object boundaries, cast masses and zedfunc stored values back to `np.float32`.

Every public function must reject:

```text
NaN
+inf
-inf
```

No warning-only behavior. Invalid numeric input fails loudly.

Recommended constants:

```python
MAX_EXACT_POINTS = 200_000
DEFAULT_TAIL_EPSILON = 2e-5
MASS_ATOL = 1e-5
MIN_RANVAR_VALUE = -67_108_800
MAX_RANVAR_VALUE = 67_108_800
```

---

## 4. Error handling and validation

Create custom exceptions that inherit from standard exceptions:

```python
class SupplyChainProbError(Exception): ...
class ValidationError(ValueError, SupplyChainProbError): ...
class DomainError(ValueError, SupplyChainProbError): ...
class FractionalValueError(ValueError, SupplyChainProbError): ...
```

At minimum, tests should assert `ValueError` for invalid user input.

Centralize validation in `_validation.py`.

Recommended helpers:

```python
def require_finite_number(x, name: str) -> float: ...
def require_integer(x, name: str, *, context: str | None = None) -> int: ...
def require_non_negative_weight(x, name: str) -> float: ...
def require_probability(x, name: str) -> float: ...
def clamp_zero_inflation(x, name: str = "zeroInflation") -> float: ...
def require_domain(low: int, high: int) -> None: ...
def ensure_same_length(*arrays, names: Sequence[str]) -> None: ...
```

Integer validation policy:

Any argument that semantically represents a quantity, bucket bound, support value, observation, stock position, period index, or zedfunc evaluation index must be integer-valued.

Accept:

```python
3
np.int64(3)
3.0
np.float32(3.0)
```

Reject:

```python
3.2
0.8
np.float32(0.8)
np.nan
np.inf
-np.inf
```

Fractional error messages should be explicit. Examples:

```text
dirac(0.8): fractional arguments are not supported.
```

```text
'uniform.left(n)' is rounding fractional numbers.
```

Required invalid-input tests:

```python
dirac(0.8)
dirac(MAX_RANVAR_VALUE + 1)
ranvar([1, 2.2])
ranvar([1, np.nan])
ranvar([1, np.inf])
ranvar([1], weights=[-1])
ranvar.buckets([1], [0.1], [2])
ranvar.buckets([1], [0], [2.2])
ranvar.buckets([1], [3], [2])
ranvar.buckets([1, 1], [0, 1], [1, 2])
ranvar.uniform(1.2)
ranvar.uniform(5, 4)
poisson(-1)
poisson(1_000_001)
negativeBinomial(0, 2)
negativeBinomial(2, 0.9)
quantile(poisson(3), -0.1)
quantile(poisson(3), 1.1)
int(poisson(3), 0.1, 2)
int(poisson(3), 3, 2)
valueAt(linear(1), 1.5)
uniform.left(0.2)
truncate(poisson(3), 9, 7)
pricebrk.f(10, [5, 5], [9, 8])
pricebrk.f(10, [10, 5], [8, 9])
pricebrk.f(10, [5.5], [9])
pricebrk.f(10, [5], [np.nan])
fit_zinb([1, 2.2])
montecarlo(0, seed=42, step=..., accumulators=[])
```

Error messages should be clear enough for business users. Do not expose obscure numpy/scipy tracebacks as the public API behavior.

---

## 5. Bankers rounding policy

Do not use rounding to accept fractional constructor inputs.

Use bankers rounding only when converting computed real values back to integer support in operations such as:

```text
transform(r, a)
fractional convolution power approximation
explicit simulation-derived rounding if a caller implements it in a simulation step
```

Use the actual binary floating value. Do not attempt decimal-rational correction.

Implement:

```python
def bankers_round_to_int(x: float | np.ndarray) -> int | np.ndarray:
    ...
```

It must use round-half-to-even behavior. `np.rint` is acceptable. Since the package stores numbers as float32, operations that conceptually use package numbers should first cast scaling values to `np.float32`.

Tests:

```python
bankers_round_to_int(0.5) == 0
bankers_round_to_int(1.5) == 2
bankers_round_to_int(2.5) == 2
bankers_round_to_int(3.5) == 4
```

---

## 6. Canonical bucket grid

A `Ranvar` is a compressed probability distribution over integers.

The ranvar domain is bounded:

```python
MIN_RANVAR_VALUE = -67_108_800
MAX_RANVAR_VALUE = 67_108_800
```

Any explicit creation or operation that produces support outside this domain must fail with an error of the form:

```text
Cannot create ranvar with domain [x .. y].
```

The canonical bucket grid is fixed and must be implemented exactly.

### 6.1 Positive side

Positive-side canonical buckets include zero.

```text
0..64           width 1, 65 buckets
65..192         width 2, 64 buckets
193..448        width 4, 64 buckets
449..960        width 8, 64 buckets
961..1984       width 16, 64 buckets
...
up to 67,108,800
```

Exact formula:

```python
# singletons
[0, 0], [1, 1], ..., [64, 64]

# widening groups
for j in range(1, 20):  # inclusive 1..19
    width = 2 ** j
    start = 128 * (2 ** (j - 1)) - 63

    for i in range(64):
        low = start + i * width
        high = start + (i + 1) * width - 1
```

The final positive bucket must end exactly at `67_108_800`.

### 6.2 Negative side

The negative side is the mirror of the positive side, excluding zero.

For every positive bucket `[low, high]` with `low > 0`, the mirrored negative bucket is:

```text
[-high, -low]
```

Examples:

```text
[1, 1]      -> [-1, -1]
[64, 64]    -> [-64, -64]
[65, 66]    -> [-66, -65]
[99, 100]   -> [-100, -99]
[993, 1008] -> [-1008, -993]
```

The full canonical grid sorted ascending starts at `-67_108_800` and ends at `67_108_800`.

Expected bucket counts:

```text
positive including zero: 1281 buckets
negative excluding zero: 1280 buckets
total: 2561 buckets
```

### 6.3 Bucket lookup examples

These examples must be unit-tested:

```python
bucket_for_value(0)     == (0, 0)
bucket_for_value(64)    == (64, 64)
bucket_for_value(65)    == (65, 66)
bucket_for_value(66)    == (65, 66)
bucket_for_value(99)    == (99, 100)
bucket_for_value(100)   == (99, 100)
bucket_for_value(192)   == (191, 192)
bucket_for_value(193)   == (193, 196)
bucket_for_value(448)   == (445, 448)
bucket_for_value(449)   == (449, 456)
bucket_for_value(960)   == (953, 960)
bucket_for_value(961)   == (961, 976)
bucket_for_value(1000)  == (993, 1008)

bucket_for_value(-1)    == (-1, -1)
bucket_for_value(-64)   == (-64, -64)
bucket_for_value(-65)   == (-66, -65)
bucket_for_value(-100)  == (-100, -99)
bucket_for_value(-1000) == (-1008, -993)
```

### 6.4 Bucket-grid tests

Test:

```text
domain bounds
bucket count
positive groups
negative mirror
lookup examples
coverage has no gaps
coverage has no overlaps
first bucket starts at MIN_RANVAR_VALUE
last bucket ends at MAX_RANVAR_VALUE
```

---

## 7. Ranvar concept

A `Ranvar` represents an approximate probability distribution over integers.

It is compressed into canonical integer buckets. Mass is stored per bucket. Within a bucket, mass is interpreted as uniformly spread across all integers in the inclusive bucket.

For bucket `[low, high]` with mass `m`:

```text
width = high - low + 1
P(X = k) = m / width, for low <= k <= high
```

This affects:

```text
mean
variance
cdf
quantile
integral
sampling
display
plotting
convolution
transform
truncate
crps
fillrate
```

Implement:

```python
@dataclass(frozen=True)
class Ranvar:
    lows: np.ndarray     # int64, inclusive lower bucket bounds
    highs: np.ndarray    # int64, inclusive upper bucket bounds
    masses: np.ndarray   # float32, total probability mass per bucket
```

Validation invariants:

```text
lows/highs/masses have the same length
lows and highs are int64
masses are float32
low <= high for every bucket
buckets sorted by low ascending
buckets non-overlapping
masses >= 0
sum(masses) approximately 1
support inside ranvar domain
```

Expose methods:

```python
class Ranvar:
    def support_min(self) -> int: ...
    def support_max(self) -> int: ...
    def mean(self) -> float: ...
    def variance(self) -> float: ...
    def dispersion(self) -> float: ...
    def quantile(self, p: float) -> int: ...
    def integral(self, low: int, high: int) -> float: ...
    def cdf_at(self, k: int) -> float: ...
    def cdf(self) -> Zedfunc: ...
    def sample(self, n: int, seed: int | None = None) -> np.ndarray: ...
    def extend_ranvar(
        self,
        gap: int | None = None,
        multiplier: int | None = None,
        reach: int | None = None,
        *,
        include_mass: bool = True,
    ) -> pd.DataFrame: ...
    def to_dataframe(self, include_zero_buckets: bool = False) -> pd.DataFrame: ...
    def plot_pmf(self, ax=None, *, density: bool = True): ...
    def plot_cdf(self, ax=None): ...
```

Also expose top-level aliases:

```python
quantile(r, p)
integral(r, low, high)
int(r, low, high)
cdf(r)
transform(r, a)
```

Top-level `mean`, `variance`, and `dispersion` may be implemented if useful, but they are not mandatory public exports.

---

## 8. Ranvar constructors

### 8.1 `dirac(n)`

```python
def dirac(n: int) -> Ranvar:
    ...
```

Rules:

```text
n must be integer-valued
n must be finite
n must be inside ranvar domain
fractional n fails
mass is assigned to the canonical bucket containing n
mass is uniform within that bucket
```

Important compressed-tail behavior:

```python
dirac(0)    -> bucket [0, 0] with mass 1
dirac(64)   -> bucket [64, 64] with mass 1
dirac(65)   -> bucket [65, 66] with mass 1
dirac(100)  -> bucket [99, 100] with mass 1
dirac(1000) -> bucket [993, 1008] with mass 1
```

Since mass is uniform inside the bucket:

```python
r = dirac(100)
r.support_min() == 99
r.support_max() == 100
quantile(r, 0.0) == 99
quantile(r, 0.5) == 99
quantile(r, 1.0) == 100
int(r, 99, 99) == 0.5
int(r, 100, 100) == 0.5
r.mean() == 99.5
r.variance() == 0.25
```

This is intentional. Do not turn compressed-tail diracs into exact point masses.

`dirac(0.8)` must fail with a fractional-argument error.

### 8.2 `ranvar(values, weights=None)`

This is the empirical ranvar constructor and aggregator.

```python
ranvar(values: Iterable[int], weights: Iterable[float] | None = None) -> Ranvar
```

Rules:

```text
values must be integer-valued
fractional observations fail
NaN/infinite observations fail
weights, if provided, must be finite and non-negative
negative weights fail
length mismatch fails
empty input returns dirac(0)
zero total weight returns dirac(0)
weights are normalized so mass sums to 1
each observation maps to its canonical bucket
mass is uniform within each bucket
```

Do not round empirical observations. This package intentionally rejects fractional observations because the domain is quantities in units.

Examples:

```python
ranvar([1, 2]).mean() == pytest.approx(1.5)
ranvar([1, 2], weights=[1.0, 2.0]).mean() == pytest.approx(1.6666667)
ranvar([], weights=[]).mean() == 0.0
ranvar([1, 2], weights=[0.0, 0.0]).mean() == 0.0
```

### 8.3 Grouped empirical aggregation

Implement:

```python
ranvar.groupby(values, groups, weights=None) -> dict[Any, Ranvar]
```

Also implement a DataFrame helper:

```python
ranvar.aggregate(
    df: pd.DataFrame,
    value_col: str,
    by: str | list[str],
    weight_col: str | None = None,
) -> pd.DataFrame
```

Rules are the same as `ranvar(...)`.

`ranvar.aggregate` should return a DataFrame with grouping columns plus one column:

```text
Ranvar
```

containing `Ranvar` objects.

### 8.4 `ranvar.buckets(weight, low, high)`

```python
ranvar.buckets(weight, low, high) -> Ranvar
```

Accept scalar or vector-like inputs. Treat all inputs as one aggregation group.

Rules:

```text
low/high must be integer-valued
low <= high for every bucket
bounds must be inside ranvar domain
weights must be finite and non-negative
negative weights fail
NaN/infinite values fail
buckets must not overlap
zero total weight returns dirac(0)
weights are normalized
input bucket mass is uniformly spread over its inclusive [low, high] segment
then accumulated into canonical buckets proportionally to overlap length
```

Required examples:

```python
r = ranvar.buckets(
    weight=[0.4, 0.6],
    low=[0, 2],
    high=[1, 3],
)
r.mean() == pytest.approx(1.7)
```

Explanation:

```text
[0,1] weight 0.4 -> values 0 and 1 each receive 0.2
[2,3] weight 0.6 -> values 2 and 3 each receive 0.3
mean = 0*0.2 + 1*0.2 + 2*0.3 + 3*0.3 = 1.7
```

Another required example:

```python
r = ranvar.buckets([1.0], [0], [2])
r.mean() == pytest.approx(1.0)
```

### 8.5 `ranvar.uniform`

```python
ranvar.uniform(n)
ranvar.uniform(m, n)
```

Rules:

```text
one-argument overload: discrete uniform on [0, n]
two-argument overload: discrete uniform on [m, n]
bounds must be integer-valued
m <= n
bounds inside domain
fractional bounds fail
mass is uniform over all integers in the segment, then compressed into canonical buckets
```

Tests:

```python
ranvar.uniform(0).mean() == 0
ranvar.uniform(1).mean() == pytest.approx(0.5)
ranvar.uniform(3).mean() == pytest.approx(1.5)
ranvar.uniform(10).mean() == pytest.approx(5)

ranvar.uniform(-1, 0).mean() == pytest.approx(-0.5)
ranvar.uniform(0, 1).mean() == pytest.approx(0.5)
ranvar.uniform(1, 3).mean() == pytest.approx(2)
ranvar.uniform(5, 10).mean() == pytest.approx(7.5)
```

---

## 9. Internal bucket accumulation

Implement internal helpers in `buckets.py` or `ranvar.py`.

```python
def accumulate_uniform_segment(
    low: int,
    high: int,
    weight: float,
    out: dict[tuple[int, int], float],
) -> None:
    ...
```

It should:

```text
validate low/high domain
find canonical buckets overlapping [low, high]
for each overlap:
    contribution = weight * overlap_width / segment_width
    add to canonical bucket
```

Use this for:

```text
ranvar.buckets
ranvar.uniform
truncate
distribution constructors
compressed transform fallback
```

Implement:

```python
def ranvar_from_bucket_mass_map(
    mass_by_bucket: Mapping[tuple[int, int], float]
) -> Ranvar:
    ...
```

Rules:

```text
drop exact zero masses
if no positive mass -> dirac(0)
reject negative masses below tolerance
clip tiny negative numerical noise only if abs(value) < 1e-12
normalize with float64
cast to float32
sort by low
validate
```

Do not silently fix meaningful negative masses.

Implement point expansion helper:

```python
def to_point_pmf(
    r: Ranvar,
    max_points: int = MAX_EXACT_POINTS,
) -> tuple[np.ndarray, np.ndarray]:
    ...
```

Rules:

```text
expand each bucket into integer points with mass/width
if total point count > max_points, raise a controlled internal exception
```

Use for exact convolution, transform, CRPS, and small-support tests when feasible.

Where exact point expansion is too large:

```text
prefer bucket/CDF math over random approximations
fallback approximations must be deterministic
always preserve mass normalization
always preserve domain
```

---

## 10. Distribution constructors

### 10.1 `poisson(lambda_)`

```python
poisson(lambda_: float) -> Ranvar
```

Rules:

```text
lambda must be finite
lambda must be non-negative
lambda greater than 1_000_000 fails
lambda == 0 returns dirac(0)
construct a finite compressed ranvar
truncate negligible tail and normalize mass
use canonical buckets
do not iterate over millions of individual points for large lambda
```

Implementation guidance:

- Use `scipy.stats.poisson`.
- Compute bucket masses using CDF differences over canonical buckets.
- Use `tail_epsilon = 2e-5` by default.
- For `poisson(3)`, maximum support should be around 12.
- Use float64 internally, cast masses to float32 at the end.

Unit tests:

```python
p = poisson(3)
p.mean() == pytest.approx(3, abs=5e-3)
p.variance() == pytest.approx(3, abs=5e-2)

quantile(poisson(3), 0.10) == 1
quantile(poisson(3), 0.50) == 3
quantile(poisson(3), 0.75) == 4
quantile(poisson(3), 0.99) == 8
quantile(poisson(3), 1.00) == 12
```

Use tolerances where compression makes exact equality inappropriate.

### 10.2 `negativeBinomial(mu, dispersion, zeroInflation=None)`

```python
negativeBinomial(mu: float, dispersion: float) -> Ranvar
negativeBinomial(mu: float, dispersion: float, zeroInflation: float) -> Ranvar
```

Rules:

```text
mu must be finite and positive
dispersion must be finite and >= 1
zeroInflation, if provided, is clamped to [0, 0.999]
zeroInflation is additional mass at zero
the base negative binomial already has mass at zero
final P(0) = alpha + (1 - alpha) * base_P(0)
final P(k>0) = (1 - alpha) * base_P(k)
final mean = (1 - alpha) * base mean
if dispersion < 1.001, use Poisson branch for likelihood and distribution approximation
```

Parameterization:

```text
r = mu / (dispersion - 1)
p_failure = 1 - 1 / dispersion
p_success = 1 / dispersion
```

PMF:

```text
P(k) = exp(
    logGamma(k+r)
  - logGamma(k+1)
  - logGamma(r)
  + k * log(p_failure)
  + r * log(p_success)
)
```

For scipy, this corresponds to:

```python
scipy.stats.nbinom(n=r, p=p_success)
```

Construct bucket masses through CDF differences.

Tests:

```python
negativeBinomial(2, 1.5).mean() == pytest.approx(2, abs=5e-3)
negativeBinomial(5, 2.0).mean() == pytest.approx(5, abs=5e-3)
negativeBinomial(2, 1.5, 0.2).mean() == pytest.approx(1.6, abs=5e-3)
```

---

## 11. Ranvar operations

### 11.1 Mean, variance, dispersion

Because bucket mass is uniform within each bucket:

For bucket `[a, b]`:

```text
width = b - a + 1
bucket_mean = (a + b) / 2
bucket_variance = (width^2 - 1) / 12
```

Overall:

```text
E[X] = sum mass_i * bucket_mean_i
Var[X] = sum mass_i * (bucket_variance_i + bucket_mean_i^2) - E[X]^2
Dispersion = variance / mean
```

If mean is zero or near zero:

```text
if abs(mean) < tiny:
    return 0.0
```

### 11.2 `quantile(r, p)`

```python
quantile(d: Ranvar, p: float) -> int
```

Rules:

```text
p must be finite
p must be in [0, 1]
p == 0 returns support_min
p == 1 returns support_max
return the smallest integer k such that P[X <= k] >= p
inside a multi-integer bucket, use uniform mass per integer
```

Invalid p error:

```text
quantile(d,p): invalid value {p} for p, should be in [0, 1].
```

### 11.3 `int` / `integral`

```python
integral(r: Ranvar, low: int, high: int) -> float
int(r: Ranvar, low: int, high: int) -> float
```

Rules for ranvars:

```text
low/high must be integer-valued
fractional bounds fail
NaN/infinite fail
low > high fails
return P[low <= X <= high]
bucket contribution = mass * overlap_width / bucket_width
```

Examples:

```python
r = poisson(3)
int(r, 0, 0) == pytest.approx(0.0498, abs=1e-3)
int(r, 0, 2) == pytest.approx(0.4232, abs=1e-3)
int(r, 2, 4) == pytest.approx(0.6161, abs=1e-3)
```

Rules for zedfuncs are in the zedfunc section.

### 11.4 `cdf`

```python
cdf(r: Ranvar) -> Zedfunc
```

Return a zedfunc mapping integer `k` to:

```text
P[X <= k]
```

CDF zedfunc behavior:

```text
k below support -> 0
k above support -> 1
integer k inside support -> discrete cumulative probability
```

Do not expand huge supports to materialize every CDF value. Use a formula-backed zedfunc where needed.

### 11.5 Sampling

```python
r.sample(n, seed=None) -> np.ndarray
```

Rules:

```text
n must be a non-negative integer
seeded draws must be reproducible across machines for the same package/dependency version
do not use global np.random state
sample a bucket by cumulative mass
then sample uniformly among integers inside that bucket
return int64 array
```

Use a local RNG:

```python
np.random.default_rng(seed)
```

### 11.6 Arithmetic

Implement:

```python
r1 + r2
r1 + integer
integer + r1

r1 - r2
r1 - integer
integer - r1

r1 * r2
r1 * integer
integer * r1

-r

r ** n
r ^ n
```

Rules:

```text
ranvar arithmetic assumes independent random variables
numbers combined with ranvars are promoted to dirac numbers
fractional numbers cannot be promoted to dirac and must fail
```

Addition:

```text
X + Y
```

Subtraction:

```text
X - Y = X + (-Y)
```

Multiplication:

```text
X * Y
```

Use exact expansion when feasible. Add guardrails:

```python
MAX_EXACT_POINTS = 200_000
```

If support expansion would exceed the threshold:

- use a deterministic compressed approximation
- do not allocate huge arrays across the full ranvar domain
- test that mass remains normalized and support remains valid

For common small/medium supports, exact convolution should be used.

### 11.7 `transform(r, a)`

```python
transform(r: Ranvar, a: float) -> Ranvar
```

Semantics:

```text
X ~ r
transform(r, a) = distribution of bankers_round(a * X)
```

Rules:

```text
a must be finite
a may be non-integer
use bankers rounding on actual binary float32 value
output support must remain inside domain
fractional constructor rules do not apply here because this is a transformation
```

Test:

```python
r = poisson(2)
t = transform(r, 3)
t.mean() == pytest.approx(5.864435, abs=0.05)
```

Use tolerant tests because compression/tail cutoffs may shift final decimals.

### 11.8 Convolution power

Implement both Python operators:

```python
r ** exponent
r ^ exponent
```

`^` is a compatibility convenience. `**` is idiomatic Python. They should call the same implementation.

Rules:

```text
exponent must be finite
negative exponents fail
r ** 0 -> dirac(0)
r ** 1 -> r
positive integer exponent -> repeated independent convolution
positive real exponent -> fractional approximation
```

Integer exponent implementation:

- Use exponentiation by squaring when reasonable.
- Use convolution guardrails.

Fractional exponent approximation:

For exponent `a`:

```text
if a is integer:
    exact repeated convolution

if a > 1 and not integer:
    r ** floor(a) convolved with r ** frac(a)

if 0 < a < 1:
    component1 = transform(r, a * (1 - a))
    component2:
        if dispersion(r) <= 1.001:
            poisson(mean(r) * a * a)
        else:
            negativeBinomial(mean(r) * a * a, dispersion(r))
    result = component1 + component2
```

Golden test from reference run:

```python
r = poisson(20) ^ 0.5

r.mean() == pytest.approx(10, abs=0.25)
quantile(r, 0.50) == 10
quantile(r, 0.90) == 13
quantile(r, 0.99) == 16
```

Prefer to tune the implementation to hit these quantiles exactly.

---

## 12. `extend.ranvar`

Implement both method and namespace function:

```python
r.extend_ranvar(
    gap: int | None = None,
    multiplier: int | None = None,
    reach: int | None = None,
    *,
    include_mass: bool = True,
) -> pd.DataFrame

extend.ranvar(r, gap=None, multiplier=None, reach=None, *, include_mass=True) -> pd.DataFrame
```

Default behavior without optional arguments:

Return the canonical bucket grid covering the materialized support.

Rules:

```text
If support is exactly zero:
    return [0, 0]

If support is strictly positive:
    start at [0, 0]
    end at the canonical bucket containing support_max

If support is strictly negative:
    start at the canonical bucket containing support_min
    end at [-1, -1]

If support crosses zero:
    start at the canonical bucket containing support_min
    end at the canonical bucket containing support_max
```

The output must include at least:

```text
Min
Max
```

If `include_mass=True`, also include:

```text
Mass
Width
Density
BucketMean
CdfLow
CdfHigh
```

Where:

```text
Mass = int(r, Min, Max)
Width = Max - Min + 1
Density = Mass / Width
BucketMean = (Min + Max) / 2
CdfLow = P[X <= Min - 1]
CdfHigh = P[X <= Max]
```

Required tests:

```python
extend.ranvar(dirac(0)) has one row: Min=0, Max=0

extend.ranvar(dirac(1000)):
    first row Min=0, Max=0
    last row Min=993, Max=1008

extend.ranvar(dirac(-1000)):
    first row Min=-1008, Max=-993
    last row Min=-1, Max=-1
```

Do not infer that support stops at `1008`; that is only the bucket containing `1000`. The global domain continues to `67_108_800`.

Optional overloads:

```python
extend.ranvar(r, gap)
extend.ranvar(r, gap, multiplier)
extend.ranvar(r, gap, multiplier, reach)
```

Implement practical behavior:

```text
gap must be integer >= 0
multiplier, if provided, must be integer >= 1
reach, if provided, must be integer

For custom overloads:
    intended for non-negative support/reorder grids
    fail if support_min < 0 to avoid silent wrong behavior

gap forces initial buckets:
    [0, 0]
    [1, gap], if gap >= 1

multiplier controls fixed bucket width after gap.
reach ensures the final bucket reaches at least reach.
```

Roundtrip test:

```python
r = poisson(3)
g = extend.ranvar(r)
r2 = ranvar.buckets(g["Mass"], g["Min"], g["Max"])

r2.mean() == pytest.approx(r.mean(), abs=1e-3)
r2.variance() == pytest.approx(r.variance(), abs=1e-2)
quantile(r2, 0.5) == quantile(r, 0.5)
```

---

## 13. Zedfunc

A `Zedfunc` represents a real-valued function over integer inputs.

```python
class Zedfunc:
    def valueAt(self, k: int) -> float: ...
    def integral(self, low: int, high: int) -> float: ...
    def to_dataframe(self, low: int, high: int) -> pd.DataFrame: ...
    def plot(self, low: int, high: int, ax=None): ...
```

Top-level:

```python
valueAt(z, k)
int(z, low, high)
integral(z, low, high)
```

Rules:

```text
k must be integer-valued
fractional k fails
NaN/infinite fails
return value may be non-integer float
bounded finite zedfuncs return 0 outside support
formula zedfuncs may define behavior everywhere
```

Intentional package decision:

- Do not implement fractional interpolation for `valueAt`.
- This package requires integer `k`.

### 13.1 Zedfunc implementation approach

Implement a flexible class that can represent:

```text
bounded arrays with low/high support and values
formula-backed functions
arithmetic compositions
```

Acceptable implementation:

```python
@dataclass(frozen=True)
class Zedfunc:
    _func: Callable[[int], float]
    low: int | None = None
    high: int | None = None
    name: str | None = None
```

For bounded zedfuncs, store compact `np.float32` values and return 0 outside `[low, high]`.

For formula-backed zedfuncs, evaluate the function at integer `k`.

### 13.2 Zedfunc constructors

Implement:

```python
constant(a) -> Zedfunc
linear(a) -> Zedfunc
uniform.left(n) -> Zedfunc
```

Rules:

```text
constant(a): valueAt(k) = a for every integer k
linear(a): valueAt(k) = a * k for every integer k
uniform.left(n): valueAt(k) = 1 if k <= n else 0
```

`constant(a)` and `linear(a)` accept finite real numbers.

`uniform.left(n)`:

```text
n must be integer-valued
fractional n fails
```

Tests:

```python
valueAt(constant(3), -1) == 3
valueAt(constant(3), 0) == 3
valueAt(constant(3), 1) == 3

valueAt(linear(2), 0) == 0
valueAt(linear(2), 1) == 2
valueAt(linear(2), 3) == 6

valueAt(uniform.left(0), -1) == 1
valueAt(uniform.left(0), 0) == 1
valueAt(uniform.left(0), 1) == 0
```

### 13.3 Zedfunc arithmetic

Implement pointwise arithmetic:

```python
z1 + z2
z1 - z2
z1 * z2
z1 / z2
-z

z + number
number + z
z - number
number - z
z * number
number * z
z / number
number / z
```

Numbers are promoted to constant zedfuncs. Numeric zedfunc constants may be non-integer.

Handle divide-by-zero with a clear `ZeroDivisionError` for scalar zero denominators. For pointwise denominators that evaluate to zero, either raise at evaluation time or return Python/numpy infinity consistently. Prefer raising at evaluation time for clarity.

### 13.4 Zedfunc integral

```python
integral(z: Zedfunc, low: int, high: int) -> float
int(z: Zedfunc, low: int, high: int) -> float
```

Rules:

```text
low/high must be integer-valued
fractional bounds fail
low > high fails
return sum(valueAt(z, k) for k in low..high)
```

Tests:

```python
z = constant(5) - linear(1)

int(z, 0, 1) == 9   # 5 + 4
int(z, 2, 4) == 6   # 3 + 2 + 1
```

---

## 14. Price breaks

Implement a `pricebrk` namespace with:

```python
pricebrk.f(initPrice, qty, newPrice) -> Zedfunc
pricebrk.m(initPrice, qty, newPrice) -> Zedfunc
```

Input format:

```python
initPrice: float
qty: Sequence[int]
newPrice: Sequence[float]
```

Validation:

```text
initPrice must be finite and >= 0
qty/newPrice must have the same length
qty must be positive integer-valued
qty must be strictly increasing in the order provided
duplicate qty fails
unsorted qty fails
newPrice values must be finite and >= 0
NaN/infinite fails
invalid input must fail, not be sorted/repaired silently
```

For both returned zedfuncs:

```text
valueAt(k) for k <= 0 returns 0
valueAt(k) for k > 0 returns marginal purchase unit price for the kth unit
```

### 14.1 Fiscal price breaks: `pricebrk.f`

Fiscal interpretation:

```text
reduced price applies only to units from the breakpoint onward
```

Example:

```python
z = pricebrk.f(10, [5, 10], [9, 8])
```

Expected:

```python
[valueAt(z, k) for k in range(1, 13)] == [
    10, 10, 10, 10,
    9, 9, 9, 9, 9,
    8, 8, 8,
]
```

### 14.2 Merchant price breaks: `pricebrk.m`

Merchant interpretation:

```text
once a breakpoint is reached, the lower unit price applies retroactively
to all units in the order
```

Define:

```text
unit_price(q) = applicable unit price for total order quantity q
total_cost(q) = q * unit_price(q)
marginal_price(q) = total_cost(q) - total_cost(q - 1)
```

Example:

```python
z = pricebrk.m(10, [5, 10], [9, 8])
```

Expected:

```python
[valueAt(z, k) for k in range(1, 13)] == [
    10, 10, 10, 10,
    5, 9, 9, 9, 9,
    -1, 8, 8,
]
```

Cumulative total tests:

```python
z = pricebrk.m(10, [5, 10], [9, 8])

int(z, 1, 4) == 40
int(z, 1, 5) == 45
int(z, 1, 9) == 81
int(z, 1, 10) == 80
int(z, 1, 12) == 96
```

Fiscal total tests:

```python
z = pricebrk.f(10, [5, 10], [9, 8])

int(z, 1, 4) == 40
int(z, 1, 5) == 49
int(z, 1, 9) == 85
int(z, 1, 10) == 93
int(z, 1, 12) == 109
```

---

## 15. Additional v1 functions

Implement these in v1:

```text
crps
fillrate
mixture
truncate
constant
linear
uniform.left
```

Do not implement or export these in v1:

```text
smooth
stockrwd.*
diracz
uniform.right
zoz
```

---

## 16. `mixture`

Implement:

```python
mixture(ranvars: Sequence[Ranvar], weights: Sequence[float] | None = None) -> Ranvar
mixture(r1: Ranvar, p1: float, r2: Ranvar) -> Ranvar
mixture(r1: Ranvar, p1: float, r2: Ranvar, p2: float, r3: Ranvar) -> Ranvar
mixture(r1: Ranvar, p1: float, r2: Ranvar, p2: float, r3: Ranvar, p3: float, r4: Ranvar) -> Ranvar
```

Python implementation can use `*args` if clean.

Aggregator/list rules:

```text
empty ranvar list -> dirac(0)
weights None -> equal weights
weights provided -> finite, non-negative, same length
zero total weight -> dirac(0)
weights normalized to sum to 1
```

Pure overload rules:

```text
mixture(r1, p1, r2):
    weights = [p1, 1 - p1]
    require 0 <= p1 <= 1

mixture(r1, p1, r2, p2, r3):
    weights = [p1, p2, 1 - p1 - p2]
    require all weights >= 0

mixture(r1, p1, r2, p2, r3, p3, r4):
    weights = [p1, p2, p3, 1 - p1 - p2 - p3]
    require all weights >= 0
```

Example:

```python
r1 = poisson(1)
r2 = poisson(3)
mixture(r1, 0.25, r2).mean() == pytest.approx(2.5, abs=0.05)
```

---

## 17. `truncate`

```python
truncate(d: Ranvar, low: int, high: int) -> Ranvar
```

Rules:

```text
low/high must be integer-valued
fractional bounds fail
low > high fails
returns the conditional ranvar restricted to [low, high]
redistributes/renormalizes mass inside [low, high]
does not pile mass onto the bounds
if low is above support_max, return dirac(low)
if high is below support_min, return dirac(high)
output support must remain inside domain
```

Intentional package decision:

- Decimal bounds are not supported.
- Do not implement floor/ceiling of decimal bounds.

Test:

```python
d = ranvar.uniform(1, 6)
d_trunc = truncate(d, 2, 4)
d.mean() == pytest.approx(3.5)
d_trunc.mean() == pytest.approx(3)
```

Error message style:

```text
truncate(_, 9, 7): expected 9 smaller or equal to 7.
```

---

## 18. `fillrate`

```python
fillrate(r: Ranvar) -> Ranvar
```

Interpretation:

The output is a ranvar representing marginal contribution to fill rate by stock position.

For strictly positive demand distribution `D`:

```text
mass at stock position k >= 1:
    P[D >= k] / E[D]

mass at k = 0:
    0
```

This makes cumulative fill rate at stock `q`:

```text
sum_{k=1..q} P[D >= k] / E[D]
= E[min(D, q)] / E[D]
```

If the input distribution has negative support, behave as if conditioning on `D > 0` first.

If there is no positive demand mass or positive mean is zero, return `dirac(0)`.

Tests for `poisson(2)`:

```python
f = fillrate(poisson(2))

int(f, 0, 0) == pytest.approx(0, abs=1e-6)
int(f, 1, 1) == pytest.approx(0.4323, abs=5e-3)
int(f, 2, 2) == pytest.approx(0.2970, abs=5e-3)
int(f, 3, 3) == pytest.approx(0.1617, abs=5e-3)
int(f, 4, 4) == pytest.approx(0.0714, abs=5e-3)

int(f, f.support_min(), f.support_max()) == pytest.approx(1.0, abs=1e-5)
```

Implementation note:

For small supports, compute point masses exactly. For large compressed supports, compute deterministic bucket approximations using CDF/survival formulas. Do not expand the full global domain.

---

## 19. `crps`

```python
crps(r: Ranvar, n: int) -> float
crps(r1: Ranvar, r2: Ranvar) -> float
```

Rules:

```text
observed value n must be integer-valued
fractional n fails
NaN/infinite fails
CRPS is sum/integral of squared CDF differences over the integer support
use finite bounded support
use uniform-within-bucket CDF semantics
```

For observation `n`, compare `r` to the step CDF:

```text
F_obs(k) = 0 if k < n else 1
```

For two ranvars, compare their CDFs over the union support.

Tests:

```python
r = poisson(3)
r1 = poisson(3)
r2 = poisson(7)

crps(r, 4) == pytest.approx(0.6826, abs=0.05)
crps(r1, r2) == pytest.approx(1.8369, abs=0.05)
```

Use tolerance because the package uses compressed support and finite tails.

---

## 20. Log-likelihood and ZINB fitting

### 20.1 `loglikelihood.negativeBinomial`

Implement namespace:

```python
loglikelihood.negativeBinomial(mean, dispersion, k)
loglikelihood.negativeBinomial(mean, dispersion, zeroInflation, k)
```

Rules:

```text
mean must be finite and > 0
dispersion must be finite and >= 1
k must be a non-negative integer
zeroInflation is clamped to [0, 0.999]
if dispersion >= 1.001 use negative-binomial branch
else use Poisson branch
```

Formula without zero inflation:

```python
if dispersion >= 1.001:
    r = mean / (dispersion - 1)
    p = 1 - 1 / dispersion
    y = (
        logGamma(k + r)
        - logGamma(k + 1)
        - logGamma(r)
        + k * log(p)
        + r * log(1 - p)
    )
else:
    y = k * log(mean) - mean - logGamma(k + 1)
```

Formula with zero inflation:

```python
alpha = clamp(zeroInflation, 0, 0.999)

if dispersion >= 1.001:
    r = mean / (dispersion - 1)
    p = 1 - 1 / dispersion

    if k == 0:
        if alpha == 0:
            y = log(1 - p) * r
        else:
            y = log(alpha + (1 - alpha) * (1 - p) ** r)
    else:
        y = (
            logGamma(k + r)
            - logGamma(k + 1)
            - logGamma(r)
            + k * log(p)
            + r * log(1 - p)
            + log(1 - alpha)
        )
else:
    if k == 0:
        y = log(alpha + (1 - alpha) * exp(-mean))
    else:
        y = poisson_loglikelihood(mean, k) + log(1 - alpha)
```

Use `scipy.special.gammaln`.

Required exact numerical tests:

```python
loglikelihood.negativeBinomial(2, 1.5, 3) == pytest.approx(-1.921965, abs=1e-6)
loglikelihood.negativeBinomial(4, 2.0, 0) == pytest.approx(-2.772589, abs=1e-6)

loglikelihood.negativeBinomial(2, 1.5, 0.2, 0) == pytest.approx(-1.027153, abs=1e-6)
loglikelihood.negativeBinomial(2, 1.5, 0.2, 3) == pytest.approx(-2.145108, abs=1e-6)
```

### 20.2 Fitting zero-inflated negative binomial

Implement:

```python
@dataclass(frozen=True)
class ZINBFit:
    mean: float
    dispersion: float
    zeroInflation: float
    loglikelihood: float
    converged: bool
    optimizer_message: str
    n_obs: int
    n_eff: float

    def to_ranvar(self) -> Ranvar: ...
```

Function:

```python
fit_zinb(
    counts,
    weights=None,
    *,
    starts: int = 20,
    seed: int | None = 0,
    method: str = "L-BFGS-B",
) -> ZINBFit
```

Validation:

```text
counts non-empty
counts finite
counts non-negative integer-valued
weights, if provided, finite and non-negative
negative weights fail
zero total weight fails for fitting
starts positive integer
```

Optimization:

Do not optimize constrained parameters directly.

Use unconstrained parameters:

```python
mean = softplus(theta_mean) + eps
dispersion = 1.0 + softplus(theta_disp)
zeroInflation = 0.999 * sigmoid(theta_zero)
```

Objective:

```text
negative weighted sum of loglikelihood.negativeBinomial(mean, dispersion, zeroInflation, k)
```

Use float64 internally.

Initial values:

```text
weighted sample mean
weighted sample variance
initial dispersion = max(var / mean, 1.001)
initial zero inflation estimated from excess zero rate, clamped
multiple random starts around this initial point
```

Tests:

1. Exact log-likelihood numerical tests above.
2. Synthetic recovery:

```python
data = negativeBinomial(4.0, 2.0, 0.25).sample(5000, seed=123)
fit = fit_zinb(data, starts=10, seed=123)

fit.converged is True
fit.mean == pytest.approx(4.0, abs=0.7)
fit.dispersion == pytest.approx(2.0, abs=0.7)
fit.zeroInflation == pytest.approx(0.25, abs=0.15)
```

Use broad tolerances because compressed distribution sampling and zero inflation can be noisy.

---

## 21. Monte Carlo block

Implement a generic Monte Carlo block abstraction. Do not implement a hard-coded action-reward simulator or a full innovation-state-space simulator in v1.

The goal is to provide:

```text
seeded reproducible simulations
streaming accumulators
avg accumulator
ranvar accumulator
debug extraction of one selected simulation
no storage of all completed trajectories by default
```

### 21.1 Public API

```python
@dataclass(frozen=True)
class SimulationContext:
    simulation_id: int
    rng: np.random.Generator
    debug: bool

@dataclass(frozen=True)
class SimulationStepResult:
    values: Mapping[str, Any]
    debug_rows: Sequence[Mapping[str, Any]] = ()

@dataclass(frozen=True)
class MonteCarloResult:
    values: Mapping[str, Any]
    debug: pd.DataFrame | None
    iterations: int
    seed: int | None
```

Function:

```python
montecarlo(
    iterations: int,
    seed: int | None,
    step: Callable[[SimulationContext], Mapping[str, Any] | SimulationStepResult],
    accumulators: Sequence[Accumulator],
    *,
    debug_simulation_id: int | None = None,
) -> MonteCarloResult
```

Accumulator constructors:

```python
avg(field: str, *, output: str | None = None) -> AvgAccumulator
ranvar_acc(field: str, *, output: str | None = None) -> RanvarAccumulator
```

Example usage:

```python
def step(ctx):
    demand = ctx.rng.poisson(3)
    reward = 2.5 * demand

    debug_rows = []
    if ctx.debug:
        debug_rows.append({
            "SimulationId": ctx.simulation_id,
            "Period": 0,
            "Demand": demand,
            "Reward": reward,
        })

    return SimulationStepResult(
        values={"demand": demand, "reward": reward},
        debug_rows=debug_rows,
    )

result = montecarlo(
    iterations=2500,
    seed=42,
    step=step,
    accumulators=[
        avg("reward"),
        ranvar_acc("demand"),
    ],
    debug_simulation_id=17,
)

result.values["reward"]  # float
result.values["demand"]  # Ranvar
result.debug             # DataFrame for simulation 17 only
```

### 21.2 Randomness model

Use deterministic per-simulation RNG streams so a specific simulation can be replayed independently.

Recommended:

```python
def make_simulation_rng(seed: int | None, simulation_id: int) -> np.random.Generator:
    if seed is None:
        # Create one random base seed for this run only.
        # The result is not reproducible when seed is None.
        ...
    return np.random.default_rng(np.random.SeedSequence([seed, simulation_id]))
```

Rules:

```text
same seed + same simulation_id + same step logic -> same path
debug extraction must not change accumulated results
debug_simulation_id is zero-based
debug_simulation_id must be in [0, iterations - 1]
iterations must be positive integer
```

### 21.3 Accumulators

`AvgAccumulator`:

```text
streaming sum and count
supports scalar numeric values
rejects NaN/infinite
result is float
```

`RanvarAccumulator`:

```text
streaming empirical ranvar construction
sampled values must be integer-valued
fractional values fail
NaN/infinite values fail
does not store all samples
accumulates canonical bucket weights/counts
final result is Ranvar
```

Vector support:

If a step value is a list, tuple, numpy array, pandas Series, or dict, support vector accumulation when clean:

```text
dict -> result is dict[key, accumulated_value]
array/list -> result is list or numpy array of accumulated values by position
```

At minimum, scalar support must be complete and tested. Vector support is strongly desirable because the target use case may accumulate one ranvar per line.

### 21.4 Debug output

Only store debug rows for the selected simulation.

Support arbitrary debug columns. The following columns should work naturally when provided by the simulation callable:

```text
SimulationId
Period
Baseline
Mean
Demand
Innovation
LevelBefore
LevelAfter
StockOnHandBefore
StockOnHandAfter
LostSales
ArrivalQuantity
ArrivalFlag
Reward
```

Unit tests:

```text
same seed gives same avg result
different seed usually gives different result
debug_simulation_id returns only rows for that simulation
running with debug_simulation_id does not alter accumulator outputs
ranvar accumulator returns a Ranvar with mass 1
no list of all trajectory values is stored on MonteCarloResult
invalid iterations fail
invalid debug id fail
fractional ranvar samples fail
```

---

## 22. Plotting and display

Implement without forcing a GUI backend:

```python
Ranvar.to_dataframe(include_zero_buckets=False)
Ranvar.plot_pmf(ax=None, *, density=True)
Ranvar.plot_cdf(ax=None)

Zedfunc.to_dataframe(low, high)
Zedfunc.plot(low, high, ax=None)
```

Use matplotlib.

Do not use seaborn.

`Ranvar.to_dataframe` columns:

```text
Min
Max
Mass
Width
Density
BucketMean
CdfLow
CdfHigh
```

Display logic:

```text
Small supports:
    bars per bucket are fine; singleton buckets behave like point masses

Wide buckets:
    when density=True, bar height should be Mass / Width
    this is visually honest for long-tail compressed buckets
```

Tests:

```text
plot methods return matplotlib axes
to_dataframe has expected columns
Mass sums to approx 1 when include_zero_buckets=False
Density equals Mass / Width
```

---

## 23. Tests: required coverage

Use pytest. Use hypothesis for a few invariants if clean.

### 23.1 Bucket grid tests

Test:

```text
domain bounds
bucket count
positive groups
negative mirror
lookup examples
coverage has no gaps
coverage has no overlaps
first bucket starts at MIN_RANVAR_VALUE
last bucket ends at MAX_RANVAR_VALUE
```

### 23.2 Construction tests

Test:

```text
dirac singleton zone
dirac compressed zone
empirical constructor
weighted empirical constructor
empty -> dirac(0)
zero weights -> dirac(0)
ranvar.buckets mean 1.7 example
ranvar.uniform examples
invalid inputs
mass normalization
dtype policy
```

### 23.3 Operation tests

Test:

```text
mean and variance formulas
quantile definition
integral overlap
cdf monotonicity
sample reproducibility
addition mean property
subtraction simple cases
multiplication simple cases
transform example
integer power examples
fractional power golden example
truncate example
mixture example
```

Property tests:

```text
mass sums to 1
masses non-negative
support within domain
CDF monotonic
quantile monotonic in p
integral(full support) == 1
mean(r1 + r2) approx mean(r1) + mean(r2)
```

### 23.4 Zedfunc tests

Test:

```text
constant
linear
uniform.left
valueAt integer-only
bounded zedfunc returns 0 outside support
arithmetic
integral
plot returns axes
```

### 23.5 Price break tests

Use exact examples:

```python
pricebrk.f(10, [5, 10], [9, 8])
pricebrk.m(10, [5, 10], [9, 8])
```

Test marginal values and cumulative totals.

Test invalid break tables fail.

### 23.6 Metrics tests

Test:

```text
fillrate poisson(2) marginal values
fillrate mass sums to 1
fillrate handles zero/no-positive demand
crps examples with tolerance
crps rejects fractional observation
```

### 23.7 Log-likelihood and fitting tests

Test exact log-likelihood values:

```text
-1.921965
-2.772589
-1.027153
-2.145108
```

Test:

```text
zeroInflation clamping
invalid k
invalid mean
invalid dispersion
fit_zinb synthetic recovery
fit_zinb invalid data
```

### 23.8 Monte Carlo tests

Test:

```text
determinism
debug extraction
debug does not alter accumulator output
avg accumulator
ranvar accumulator
invalid inputs
no all-trajectory storage
```

### 23.9 Forbidden references test

Create `tests/test_forbidden_terms.py`.

It should scan:

```text
.py
.md
.toml
.txt
.yml
.yaml
```

Ignore:

```text
.git
.venv
__pycache__
.pytest_cache
.ruff_cache
.mypy_cache
dist
build
*.egg-info
```

Construct forbidden strings dynamically:

```python
forbidden = [
    "Lo" + "kad",
    "lo" + "kad",
    "En" + "vision",
    "en" + "vision",
    "docs." + "lo" + "kad",
    "en" + "vision." + "lo" + "kad",
]
```

Fail with the offending file path and forbidden token.

---

## 24. Performance guardrails

Do not prematurely optimize, but do not write obviously bad code.

Required guardrails:

```text
Do not expand the full ranvar domain into 134 million integer points.
Do not store all Monte Carlo trajectories.
Do not compute Poisson/NB distributions by iterating every integer up to huge support.
Use canonical bucket CDF differences for large distribution constructors.
Use exact point expansion only under a configured threshold.
Use deterministic compressed approximations above the threshold.
Use float64 for cumulative sums and normalization.
Normalize mass once at object boundaries.
Avoid pandas in tight numeric kernels unless it is only for final display.
```

---

## 25. README content

README must include:

```text
project purpose
educational/non-commercial restriction
installation
quickstart
main concepts: ranvar and zedfunc
strict integer quantity policy
examples:
  poisson + quantile
  ranvar.buckets
  pricebrk.m
  montecarlo avg + ranvar accumulator
testing command
known design notes
```

Do not include forbidden source references or external documentation URLs.

Quickstart example:

```python
from supplychain_prob import poisson, quantile, int

demand = poisson(3)

print(demand.mean())
print(quantile(demand, 0.9))
print(int(demand, 0, 2))
```

Bucket example:

```python
from supplychain_prob import ranvar

r = ranvar.buckets(
    weight=[0.4, 0.6],
    low=[0, 2],
    high=[1, 3],
)

print(r.mean())  # around 1.7
```

Price break example:

```python
from supplychain_prob import pricebrk, valueAt, int

z = pricebrk.m(10, [5, 10], [9, 8])

print(valueAt(z, 5))      # 5
print(valueAt(z, 10))     # -1
print(int(z, 1, 10))      # 80
```

Monte Carlo example:

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

---

## 26. Completion checklist

Before finishing, verify:

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
mypy src
```

All should pass. If a quality gate cannot pass for an environmental reason, state exactly what failed and why.

Final repository must have:

```text
complete implementation
no placeholder tests
no skipped tests unless strongly justified
README present
LICENSE present
py.typed present
no forbidden source/product/company references
all public API imports work
all examples in README are covered by tests
```

Do not leave TODOs for core behavior. If a tradeoff is made, encode it as a documented design decision and test the chosen behavior.

Final response should summarize:

```text
files created
test commands run
test results
any intentional limitations
```
