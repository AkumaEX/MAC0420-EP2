import math
import numpy as np
from OpenGL import GL
from Source.Graphics.Actor import Actor

class Pipe(Actor):

    ## initialization
    def __init__(self, renderer,  **kwargs):
        """Initialize actor."""
        super(Pipe, self).__init__(renderer, **kwargs)

        self._radius = kwargs.get("radius", 1.0)
        self._height = kwargs.get("height", 2.0)
        self._resolution = kwargs.get("resolution", 5)

        self._vertices = None

        ## create actor
        self.initialize()
        

    @property
    def radius(self):
        """Returns the bottom radius of this cone"""
        return self._radius

    @property
    def height(self):
        """Returns the height of this cone"""
        return self._height

    
    def generateGeometry(self):
        """Creates cone geometry"""

        ## circle coordinates in x-z plane
        h2 = self._height * 0.5
        angle = np.linspace(0.0, 2.0*math.pi, self._resolution, endpoint=False)
        angle = np.append(angle, [0.0])

        ## circle in x-z plane
        x = -np.sin(angle) * self._radius
        y = np.zeros(self._resolution+1)
        z = -np.cos(angle) * self._radius

        ## normal vectors
        nx = -np.sin(angle)
        ny = np.zeros(self._resolution+1)
        nz = -np.cos(angle)

        ## side
        vertices, normals = [], []
        for i in list(range(self._resolution)):
            vertices.append([x[i], h2, z[i]])
            normals.append([nx[i], ny[i], nz[i]])

            vertices.append([x[i], -h2, z[i]])
            normals.append([nx[i], ny[i], nz[i]])
            
            vertices.append([x[i+1], h2, z[i+1]])
            normals.append([nx[i+1], ny[i+1], nz[i+1]])

            vertices.append([x[i], -h2, z[i]])
            normals.append([nx[i], ny[i], nz[i]])

            vertices.append([x[i+1], -h2, z[i+1]])
            normals.append([nx[i+1], ny[i+1], nz[i+1]])

            vertices.append([x[i+1], h2, z[i+1]])
            normals.append([nx[i+1], ny[i+1], nz[i+1]])

        vertices_side = np.array(vertices, dtype=np.float32)
        normals_side = np.array(normals, dtype=np.float32)
        self._num_vertices_side = len(vertices_side)

        self._vertices = np.concatenate((vertices_side))
        self._normals = np.concatenate((normals_side))


    def initialize(self):
        """Creates pipe geometry"""
        if self._vertices is None:
            self.generateGeometry()

        ## create object
        self.create(self._vertices, normals=self._normals)

       
    def render(self):
        """Render pipe"""
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self._num_vertices_side)

    