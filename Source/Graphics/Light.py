from PyQt5.QtCore import QObject
from PyQt5.QtGui import QVector3D, QVector4D

##  Base class for light properties.
class Light(QObject):

    ## initialization
    def __init__(self, **kwargs):
        """Initialize actor."""
        super(Light, self).__init__()

        self._headlight = kwargs.get("headlight", False)
        self._position = kwargs.get("position", QVector3D(0.0, 0.0, 0.0))
        self._ambientColor = kwargs.get("ambient", QVector3D(0.2, 0.2, 0.2))
        self._diffuseColor = kwargs.get("diffuse", QVector3D(0.8, 0.8, 0.8))
        self._specularColor = kwargs.get("specular", QVector3D(0.0, 0.0, 0.0))
        self._attenuation = kwargs.get("attenuation", QVector3D(1.0, 0.02, 0.002))
        self._directional = kwargs.get("directional", True)


    @property 
    def headlight(self):
        """Returns true if a headlight"""
        return self._headlight


    def setHeadLight(self, headlight):
        """Sets headlight on/off"""
        self._headlight = headlight


    @property 
    def directional(self):
        """Returns true if this is a directional light"""
        return self._directional


    def setDirectional(self, directional):
        """Sets whether this is directoinal light"""
        self._directional = directional


    @property 
    def position(self):
        """The position of this light in space"""
        return QVector4D(self._position[0], self._position[1], self._position[2], 1.0 - float(self._directional))


    @property
    def ambientColor(self):
        """The ambient color of this light"""
        return self._ambientColor


    @property
    def diffuseColor(self):
        """The diffusive color of this light"""
        return self._diffuseColor


    @property
    def specularColor(self):
        """The specular color of this light"""
        return self._specularColor


    @property
    def attenuation(self):
        """The quadratic, linear, and constant attenuation light factors"""
        return self._attenuation




