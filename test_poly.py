import time
from sympy import *
from magicball.model.poly import *


def print_polyhedron_data(poly):
	str_v = ', \n'.join(str(n)+': '+str(v) for n, v in enumerate(poly.vertices))
	str_f = ', \n'.join(str(n)+': '+str(f.args[0]) for n, f in enumerate(poly.faces))
	str_e = ', \n'.join(str(vfs) for vfs in poly.edges)
	str_vf = ', \n'.join(str(v)+': '+str(fs) for v, fs in poly.vertices_faces.items())
	str_fv = ', \n'.join(str(f)+': '+str(vs) for f, vs in poly.faces_vertices.items())
	str_vv = ', \n'.join(str(v)+': '+str(vs) for v, vs in poly.vertices_vertices.items())
	str_ff = ', \n'.join(str(f)+': '+str(fs) for f, fs in poly.faces_faces.items())
	print('vertices: {')
	print(str_v)
	print('}')
	print('faces: {')
	print(str_f)
	print('}')
	print('edges: {')
	print(str_e)
	print('}')
	print('vertices_faces: {')
	print(str_vf)
	print('}')
	print('faces_vertices: {')
	print(str_fv)
	print('}')
	print('vertices_vertices: {')
	print(str_vv)
	print('}')
	print('faces_faces: {')
	print(str_ff)
	print('}')

print('===== test tetra =====')
t = time.time()
tetra = ConvexPolyhedron.from_hrepr(tetrahedron)
elapsed = time.time() - t
print_polyhedron_data(tetra)
print('======================')
print('elapsed time: '+str(elapsed))
v_tetra = set(map(ImmutableMatrix, tetra.vertices))
vertices_tetra = set(simplify(v) for v in vertices_tetra)
print('test result: ' + str(v_tetra == vertices_tetra))
input('[#] ')


print('===== test octa ======')
t = time.time()
octa = ConvexPolyhedron.from_hrepr(octahedron)
elapsed = time.time() - t
print_polyhedron_data(octa)
print('======================')
print('elapsed time: '+str(elapsed))
v_octa = set(map(ImmutableMatrix, octa.vertices))
vertices_octa = set(simplify(v) for v in vertices_octa)
print('test result: ' + str(v_octa == vertices_octa))
input('[#] ')


print('===== test cube ======')
t = time.time()
cube = ConvexPolyhedron.from_hrepr(cube)
elapsed = time.time() - t
print_polyhedron_data(cube)
print('======================')
print('elapsed time: '+str(elapsed))
v_cube = set(map(ImmutableMatrix, cube.vertices))
vertices_cube = set(simplify(v) for v in vertices_cube)
print('test result: ' + str(v_cube == vertices_cube))
input('[#] ')


print('===== test dodeca ====')
t = time.time()
dodeca = ConvexPolyhedron.from_hrepr(dodecahedron)
elapsed = time.time() - t
print_polyhedron_data(dodeca)
print('======================')
print('elapsed time: '+str(elapsed))
v_dodeca = set(map(ImmutableMatrix, dodeca.vertices))
vertices_dodeca = set(simplify(v) for v in vertices_dodeca)
print('test result: ' + str(v_dodeca == vertices_dodeca))
input('[#] ')


print('===== test icosa =====')
t = time.time()
icosa = ConvexPolyhedron.from_hrepr(icosahedron)
elapsed = time.time() - t
print_polyhedron_data(icosa)
print('======================')
print('elapsed time: '+str(elapsed))
v_icosa = set(map(ImmutableMatrix, icosa.vertices))
vertices_icosa = set(simplify(v) for v in vertices_icosa)
print('test result: ' + str(v_icosa == vertices_icosa))
input('[#] ')

