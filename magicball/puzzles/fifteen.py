from sympy import *
from mathplus import *
from puzzle import *

n = 4
states = AbstractSet(lambda m: getattr(m, 'is_Matrix', False) and m.shape == (n,n) and sorted(m[:]) == list(range(0,n*n)))
operations = {( 1, 0), (-1, 0), ( 0, 1), ( 0,-1)}
def application(st, op):
	k = st.key2ij(st[:].index(0))
	m = tuple(Matrix(k)-Matrix(op))
	try:
		st2 = st[:,:]
		st2[k], st2[m] = st[m], st[k]
		return st2
	except:
		return None

system = DiscretePuzzleSystem(states, operations, application)
init = Matrix(n,n, range(1,n*n+1))
init[n-1,n-1] = 0


