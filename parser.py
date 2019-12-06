import numpy as np
import os
from pywavefront import Wavefront
from PyQt5.QtGui import *
from Source.Graphics.Material import Material
from Source.Graphics.WFOParts import WFOParts


class Parser():
    def __init__(self, filename, scene):
        self._filename = filename
        self._dirname = os.path.dirname(os.path.abspath(filename))
        self._filenames = []
        self._WFOParts = []
        self._world = scene
        self.scale = 10

    def get_WFOParts(self):

        for filename in self._get_filenames():

            scene = Wavefront(filename, create_materials=True,
                              collect_faces=True)

            for name, material in scene.materials.items():
                emission = QVector3D(*material.emissive[0:3])
                ambient = QVector3D(*material.ambient[0:3])
                diffuse = QVector3D(*material.diffuse[0:3])
                specular = QVector3D(*material.specular[0:3])
                shininess = material.shininess
                materials = Material(emission=emission, ambient=ambient,
                                     diffuse=diffuse, specular=specular, shininess=shininess)

                texcoords, normals, vertices = [], [], []
                if material.vertex_format == 'T2F_N3F_V3F':  # completo
                    all_vertices = np.array(material.vertices, dtype=np.float32).reshape(
                        (len(material.vertices)//8, 8))
                    texcoords = all_vertices[:, 0:2] / self.scale
                    normals = all_vertices[:, 2:5] / self.scale
                    vertices = all_vertices[:, 5:] / self.scale
                    part = WFOParts(self._world, vertices=vertices,
                                    normals=normals, texcoords=texcoords, material=materials)
                    self._WFOParts.append(part)
                elif material.vertex_format == 'T2F_V3F':  # sem normais
                    all_vertices = np.array(material.vertices, dtype=np.float32).reshape(
                        (len(material.vertices)//5, 5))
                    texcoords = all_vertices[:, 0:2] / self.scale
                    vertices = all_vertices[:, 2:] / self.scale
                    normals = self._calculate_normals(vertices)
                    part = WFOParts(self._world, vertices=vertices,
                                    normals=normals, texcoords=texcoords, material=materials)
                    self._WFOParts.append(part)
                elif material.vertex_format == 'N3F_V3F':  # sem textura
                    all_vertices = np.array(material.vertices, dtype=np.float32).reshape(
                        (len(material.vertices)//6, 6))
                    texcoords = self._calculate_texcoords(vertices)
                    normals = all_vertices[:, 0:3] / self.scale
                    vertices = all_vertices[:, 3:] / self.scale
                    part = WFOParts(self._world, vertices=vertices,
                                    normals=normals, texcoords=texcoords, material=materials)
                    self._WFOParts.append(part)
        self._cleanup()
        return self._WFOParts

    def _get_filenames(self):
        f = open(self._filename, 'r').readlines()

        for index, obj in enumerate(self._get_objects(f)):
            filename = '{0}/{1}_{1}.obj'.format(self._dirname, index)
            self._filenames.append(filename)
            np.savetxt(fname=filename, X=obj, fmt='%s')

        return self._filenames

    def _get_objects(self, f):
        objects = []
        i = 0
        while i < len(f):
            if i+1 == len(f) or 'f ' in f[i] and 'v ' in f[i+1]:
                obj = f[:i+1]
                objects.append(obj)

                if i+1 < len(f):
                    to_delete = []
                    for j in range(i+1):
                        if '#' in f[j] or 'o ' in f[j] or 'usemtl' in f[j] or 'f ' in f[j]:
                            to_delete.append(f[j])
                    for j in range(len(to_delete)):
                        f.remove(to_delete[j])
                    i = 0
                    continue
            i += 1
        return objects

    def _cleanup(self):
        for filename in self._filenames:
            os.remove(filename)

    def _calculate_normals(self, vertices):
        normals = []
        for i in range(0, len(vertices), 3):
            a = vertices[i]
            b = vertices[i+1]
            c = vertices[i+2]
            ab = a-b
            cb = c-b
            n = np.cross(cb, ab)
            normals.append(n)
            normals.append(n)
            normals.append(n)
        return np.array(normals).reshape(vertices.shape)

    def _calculate_texcoords(self, vertices):
        lines = len(vertices) // 3
        return np.zeros((lines, 2))
