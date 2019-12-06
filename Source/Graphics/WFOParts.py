import numpy as np

from OpenGL import GL
from Source.Graphics.Actor import Actor


class WFOParts(Actor):

    # initialization
    def __init__(self, scene, **kwargs):
        super(WFOParts, self).__init__(
            scene, mode=Actor.RenderMode.Triangles, **kwargs)

        self._vertices = kwargs.get('vertices')
        self._normals = kwargs.get('normals')
        self._texcoords = kwargs.get('texcoords')

        # create actor
        self.initialize()

    def isSelectable(self):
        """Returns true if actor is selectable"""
        return True

    def generateGeometry(self):
        """Generate geometry"""
        pass

    def initialize(self):
        """Create new geometry"""
        if self._vertices is None:
            self.generateGeometry()

        # create object
        self.create(vertices=self._vertices, normals=self._normals,
                    texcoords=self._texcoords)

    def render(self):
        """Render object"""
        GL.glDrawArrays(self._render_mode, 0, len(self._vertices))
