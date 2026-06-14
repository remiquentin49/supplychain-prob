class Series(list): pass
class DataFrame:
 def __init__(self, rows=None):
  self.rows=[] if rows is None else (rows if isinstance(rows,list) else [dict(zip(rows.keys(), vals)) for vals in zip(*rows.values())])
 def __getitem__(self,k): return Series([r[k] for r in self.rows])
 def __len__(self): return len(self.rows)
 def groupby(self, by):
  cols=by if isinstance(by,list) else [by]; d={}
  for r in self.rows:
   key=tuple(r[c] for c in cols); key=key if len(key)>1 else key[0]; d.setdefault(key,[]).append(r)
  for k,v in d.items(): yield k, DataFrame(v)
Series.sum = lambda self: sum(self)
