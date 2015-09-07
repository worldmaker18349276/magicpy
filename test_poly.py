import time
from sympy import *
from magicball.model.poly import *


print('===== test dodeca ====')
t = time.time()
vf_dodeca = to_mesh(dodecahedron)
print('======================')
print('test result:')
v_dodeca = set(map(ImmutableMatrix, vf_dodeca[0]))
vertices_dodeca = set(simplify(v) for v in vertices_dodeca)
print(v_dodeca == vertices_dodeca)
print('find vertices:')
for v in v_dodeca:
    print('    '+str(tuple(v)))
print('expected vertices:')
for v in vertices_dodeca:
    print('    '+str(tuple(v)))
elapsed = time.time() - t
print('elapsed time: '+str(elapsed))


print('===== test icosa =====')
t = time.time()
vf_icosa = to_mesh(icosahedron)
print('======================')
print('test result:')
v_icosa = set(map(ImmutableMatrix, vf_icosa[0]))
vertices_icosa = set(simplify(v) for v in vertices_icosa)
print(v_icosa == vertices_icosa)
print('find vertices:')
for v in v_icosa:
    print('    '+str(tuple(v)))
print('expected vertices:')
for v in vertices_icosa:
    print('    '+str(tuple(v)))
elapsed = time.time() - t
print('elapsed time: '+str(elapsed))

