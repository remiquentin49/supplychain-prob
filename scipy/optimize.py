class Res:
 def __init__(self,x,fun): self.x=x; self.fun=fun; self.success=True; self.message='ok'
def minimize(obj,x0,method=None): return Res(x0,obj(x0))
