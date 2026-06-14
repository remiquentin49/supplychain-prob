import math
class poisson:
 @staticmethod
 def pmf(xs,mean):
  try: return [math.exp(-mean)*mean**int(x)/math.factorial(int(x)) for x in xs]
  except TypeError: return math.exp(-mean)*mean**int(xs)/math.factorial(int(xs))
 @staticmethod
 def ppf(q,mean):
  c=0; k=0
  while c<q and k<100000:
   c+=poisson.pmf(k,mean); k+=1
  return k-1
class nbinom:
 @staticmethod
 def pmf(xs,r,p):
  def one(k): return math.exp(math.lgamma(k+r)-math.lgamma(k+1)-math.lgamma(r)+r*math.log(p)+k*math.log(1-p))
  try: return [one(int(x)) for x in xs]
  except TypeError: return one(int(xs))
