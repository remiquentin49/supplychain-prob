from .ranvar import Ranvar

def ranvar(r: Ranvar, *args, **kwargs):
    return r.extend_ranvar(*args, **kwargs)
