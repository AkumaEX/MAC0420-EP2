from PyQt5.QtGui import *

from OpenGL import GL
from Source.Graphics.Group import Group
from Source.Graphics.Material import Material
from Source.Graphics.Cone import Cone
from Source.Graphics.Icosahedron import Icosahedron
from Source.Graphics.Pipe import Pipe
import copy


class AxisMarker(Group):

    # initialization
    def __init__(self, scene, **kwargs):
        """Initialize actor."""
        super(AxisMarker, self).__init__(scene, **kwargs)
        self._transform = kwargs.get("transform", QMatrix4x4())

        self._resolution = kwargs.get("resolution", 100)
        self._colorx = kwargs.get("xcolor", QVector3D(1.0, 0.0, 0.0))
        self._colory = kwargs.get("ycolor", QVector3D(0.0, 1.0, 0.0))
        self._colorz = kwargs.get("zcolor", QVector3D(0.0, 0.47, 0.78))
        self.setSelectable(False)

        # x axis sphere
        self.addPart(Icosahedron(self.scene, name="x-axis sphere", level=2,
                                 resolution=self._resolution, material=Material(diffuse=self._colorx)))

        # y axis sphere
        self.addPart(Icosahedron(self.scene, name="y-axis sphere", level=2,
                                 resolution=self._resolution, material=Material(diffuse=self._colory)))

        # z axis sphere
        self.addPart(Icosahedron(self.scene, name="z-axis sphere", level=2,
                                 resolution=self._resolution, material=Material(diffuse=self._colorz)))

        # x axis cone
        self.addPart(Cone(self.scene, name="x-axis cone",
                          resolution=self._resolution, material=Material(diffuse=self._colorx)))

        # y axis cone
        self.addPart(Cone(self.scene, name="y-axis cone",
                          resolution=self._resolution, material=Material(diffuse=self._colory)))

        # z axis cone
        self.addPart(Cone(self.scene, name="z-axis cone",
                          resolution=self._resolution, material=Material(diffuse=self._colorz)))

        # x axis pipe
        self.addPart(Pipe(self.scene, name="x-axis pipe", radius=0.1, height=15,
                              resolution=self._resolution, material=Material(diffuse=self._colorx)))

        # y axis pipe
        self.addPart(Pipe(self.scene, name="y-axis pipe", radius=0.1, height=15,
                              resolution=self._resolution, material=Material(diffuse=self._colory)))

        # z axis pipe
        self.addPart(Pipe(self.scene, name="z-axis pipe", radius=0.1, height=15,
                              resolution=self._resolution, material=Material(diffuse=self._colorz)))

        # x axis circle
        self.addPart(Pipe(self.scene, name="x-axis circle", radius=15, height=0.5,
                          resolution=self._resolution, material=Material(diffuse=self._colorx)))

        # y axis circle
        self.addPart(Pipe(self.scene, name="y-axis circle", radius=15, height=0.5,
                          resolution=self._resolution, material=Material(diffuse=self._colory)))

        # z axis circle
        self.addPart(Pipe(self.scene, name="z-axis circle", radius=15, height=0.5,
                          resolution=self._resolution, material=Material(diffuse=self._colorz)))

        self.reset_visibility()

    def reset_visibility(self):
        for part in self.parts:
            part.setVisible(False)

    def reset_highlight(self):
        for part in self.parts:
            part.setHighlighted(False)

    def set_translate(self):
        self.reset_visibility()
        for actor in self._get_translate_actors():
            actor.setVisible(True)
        self.update('translate')

    def set_rotate(self):
        self.reset_visibility()
        for actor in self._get_rotate_actors():
            actor.setVisible(True)
        self.update('rotate')

    def set_scale(self):
        self.reset_visibility()
        for actor in self._get_scale_actors():
            actor.setVisible(True)
        self.update('scale')

    def set_axis(self, axis):
        self.reset_highlight()

        if axis == 'X':
            self.findPartByName('x-axis sphere').setHighlighted(True)
            self.findPartByName('x-axis cone').setHighlighted(True)
            self.findPartByName('x-axis pipe').setHighlighted(True)
        elif axis == 'Y':
            self.findPartByName('y-axis sphere').setHighlighted(True)
            self.findPartByName('y-axis cone').setHighlighted(True)
            self.findPartByName('y-axis pipe').setHighlighted(True)
        elif axis == 'Z':
            self.findPartByName('z-axis sphere').setHighlighted(True)
            self.findPartByName('z-axis cone').setHighlighted(True)
            self.findPartByName('z-axis pipe').setHighlighted(True)
        elif axis == 'W':
            for part in self.parts:
                part.setHighlighted(True)

    def set_rotation(self, quat):
        self.findPartByName('x-axis circle').transform().rotate(quat)
        self.findPartByName('y-axis circle').transform().rotate(quat)
        self.findPartByName('z-axis circle').transform().rotate(quat)

    def setTransform(self, xform):
        self._transform = xform

    def update(self, edit_type):

        if edit_type == 'translate':
            for actor in self._get_translate_actors():
                xform = QMatrix4x4()
                xform.translate(
                    self._transform[0, 3], self._transform[1, 3], self._transform[2, 3])
                xform.scale(0.1, 0.1, 0.1)

                axis = actor.name.split('-')[0].upper()
                if axis == 'X':
                    xform.rotate(-90.0, QVector3D(0.0, 0.0, 1.0))
                elif axis == 'Z':
                    xform.rotate(90.0, QVector3D(1.0, 0.0, 0.0))

                if isinstance(actor, Cone):
                    xform.translate(0.0, 15, 0.0)
                elif isinstance(actor, Pipe):
                    xform.translate(0.0, 7.5, 0.0)
                actor.setTransform(xform)

        elif edit_type == 'rotate':
            for actor in self._get_rotate_actors():
                xform = copy.deepcopy(self._transform)
                xform.scale(0.1, 0.1, 0.1)

                axis = actor.name.split('-')[0].upper()
                if axis == 'X':
                    xform.rotate(-90.0, QVector3D(0.0, 0.0, 1.0))
                elif axis == 'Z':
                    xform.rotate(90.0, QVector3D(1.0, 0.0, 0.0))
                actor.setTransform(xform)

        elif edit_type == 'scale':
            for actor in self._get_scale_actors():
                xform = copy.deepcopy(self._transform)
                xform.scale(0.1, 0.1, 0.1)

                axis = actor.name.split('-')[0].upper()
                if axis == 'X':
                    xform.rotate(-90.0, QVector3D(0.0, 0.0, 1.0))
                elif axis == 'Z':
                    xform.rotate(90.0, QVector3D(1.0, 0.0, 0.0))
                actor.setTransform(xform)
                if isinstance(actor, Icosahedron):
                    xform.translate(0.0, 15, 0.0)
                elif isinstance(actor, Pipe):
                    xform.translate(0.0, 7.5, 0.0)
                actor.setTransform(xform)

    def _get_translate_actors(self):
        return [
            self.findPartByName('x-axis cone'),
            self.findPartByName('y-axis cone'),
            self.findPartByName('z-axis cone'),
            self.findPartByName('x-axis pipe'),
            self.findPartByName('y-axis pipe'),
            self.findPartByName('z-axis pipe')
        ]

    def _get_rotate_actors(self):
        return [
            self.findPartByName('x-axis circle'),
            self.findPartByName('y-axis circle'),
            self.findPartByName('z-axis circle')
        ]

    def _get_scale_actors(self):
        return [
            self.findPartByName('x-axis sphere'),
            self.findPartByName('y-axis sphere'),
            self.findPartByName('z-axis sphere'),
            self.findPartByName('x-axis pipe'),
            self.findPartByName('y-axis pipe'),
            self.findPartByName('z-axis pipe')
        ]
