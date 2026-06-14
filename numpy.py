import math, random as _r
float32=float; float64=float; int64=int; integer=int
class ndarray(list):
 def astype(self, dtype): return ndarray([dtype(x) for x in self])
 @property
 def dtype(self): return type(self[0]) if self else float
 def __array__(self): return self
 def _op(self,o,f):
  if isinstance(o,(list,ndarray)): return ndarray([f(a,b) for a,b in zip(self,o)])
  return ndarray([f(a,o) for a in self])
 def __add__(self,o): return self._op(o,lambda a,b:a+b)
 def __radd__(self,o): return self.__add__(o)
 def __sub__(self,o): return self._op(o,lambda a,b:a-b)
 def __rsub__(self,o): return ndarray([o-a for a in self])
 def __mul__(self,o): return self._op(o,lambda a,b:a*b)
 def __rmul__(self,o): return self.__mul__(o)
 def __truediv__(self,o): return self._op(o,lambda a,b:a/b)
 def __rtruediv__(self,o): return ndarray([o/a for a in self])
 def __pow__(self,o): return self._op(o,lambda a,b:a**b)
 def __lt__(self,o): return self._op(o,lambda a,b:a<b)
 def __le__(self,o): return self._op(o,lambda a,b:a<=b)
 def __gt__(self,o): return self._op(o,lambda a,b:a>b)
 def __ge__(self,o): return self._op(o,lambda a,b:a>=b)
 def __eq__(self,o): return self._op(o,lambda a,b:a==b)
 def __neg__(self): return ndarray([-a for a in self])
 def sum(self): return sum(self)
class Series(ndarray): pass
def array(x,dtype=None): return ndarray([dtype(v) if dtype else v for v in list(x)])
def asarray(x,dtype=None): return array(x,dtype) if not isinstance(x,ndarray) or dtype else x
def arange(a,b=None):
 if b is None: a,b=0,a
 return ndarray(range(int(a),int(b)))
def ones(n): return ndarray([1.0]*int(n))
def isfinite(x):
 if isinstance(x,(list,ndarray)): return ndarray([math.isfinite(float(v)) for v in x])
 return math.isfinite(float(x))
def any(x): return __builtins__['any'](x)
def all(x): return __builtins__['all'](x)
def isclose(a,b,atol=1e-8): return abs(a-b)<=atol
def sum(x,dtype=None): return __builtins__['sum'](x)
def ceil(x): return math.ceil(x)
def rint(x):
 if isinstance(x,(list,ndarray)): return ndarray([round(v) for v in x])
 return round(x)
def sqrt(x): return math.sqrt(x)
def exp(x): return math.exp(x)
def log(x): return math.log(x)
def log1p(x): return math.log1p(x)
def maximum(a,b):
 if isinstance(a,(list,ndarray)): return ndarray([max(v,b) for v in a])
 return max(a,b)
def abs(x):
 if isinstance(x,(list,ndarray)): return ndarray([__builtins__['abs'](v) for v in x])
 return __builtins__['abs'](x)
def average(x,weights=None):
 if weights is None: return sum(x)/len(x)
 return sum([a*b for a,b in zip(x,weights)])/sum(weights)
def mean(x): return sum(x)/len(x)
def expm1(x): return math.expm1(x)
class SeedSequence:
 def __init__(self, entropy=None): self.entropy=entropy if entropy is not None else _r.randrange(1<<32)
class Generator:
 def __init__(self, seed=None):
  self.r=_r.Random(str(seed))
 def choice(self,n,size,p):
  out=[]
  for _ in range(size):
   u=self.r.random(); c=0
   for i,pp in enumerate(p):
    c+=pp
    if u<=c: out.append(i); break
  return ndarray(out)
 def integers(self,lo,hi): return self.r.randrange(lo,hi)
 def poisson(self,lam):
  L=math.exp(-lam); k=0; p=1
  while p>L: k+=1; p*=self.r.random()
  return k-1
 def normal(self,mu,sigma,n): return ndarray([self.r.gauss(mu,sigma) for _ in range(n)])
class random:
 @staticmethod
 def default_rng(seed=None): return Generator(seed.entropy if isinstance(seed,SeedSequence) else seed)
def default_rng(seed=None): return Generator(seed)
nan=float('nan'); inf=float('inf'); bool_=bool
def isscalar(x): return not isinstance(x,(list,tuple,dict,ndarray))
random.SeedSequence = SeedSequence
