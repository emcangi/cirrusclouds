#============================================================================#
# Create a 20 x 16 grid 
#============================================================================#

dx = 20
dy = 16
make_grid(dx, dy, (1280, 960), True)
vertices = np.loadtxt('{}x{}grid_real_vertices.txt'.format(dx,dy))
centers = np.loadtxt('{}x{}grid_centers.txt'.format(dx,dy))
fig = plt.figure(figsize=(12,9))
plt.scatter(vertices[:,0], vertices[:,1], s=7, marker='o')
plt.scatter(centers[:,0], centers[:,1], s=2, marker='+')
plt.show()