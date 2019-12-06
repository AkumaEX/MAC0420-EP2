import numpy as np
from PyQt5.QtGui import *
from OpenGL import GL
from Source.Graphics.Group import Group
from parser import Parser


class WFObject(Group):

    def __init__(self, scene, **kwargs):
        super(WFObject, self).__init__(scene, **kwargs)
        self._transform = kwargs.get("transform", QMatrix4x4())
        self._name = kwargs.get("name", "Actor"+str(id(self)))
        self.setSelectable(True)

        filename = kwargs.get('filename')
        parts = Parser(filename, self.scene).get_WFOParts()
        for part in parts:
            self.addPart(part)

        self.setTransform(self._transform)

    def setHighlighted(self, value):
        for part in self.parts:
            part.setHighlighted(value)

    def intersect(self, ray):
        results, distances = [], []
        for part in self.parts:
            result, distance = part.intersect(ray)
            results.append(result)
            distances.append(distance)
        return max(results), min(distances)

    def setTransform(self, xform):
        self._transform = xform
        for part in self.parts:
            part.setTransform(xform)

    def transform(self):
        return self._transform

    def position(self):
        xform = self.transform()
        return QVector3D(xform[0, 3], xform[1, 3], xform[2, 3])

    def setPosition(self, pos):
        self._transform = QMatrix4x4()
        self._transform.translate(pos.x(), pos.y(), pos.z())
        for part in self.parts:
            part.setPosition(pos)
