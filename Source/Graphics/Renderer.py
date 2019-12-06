import math
import numpy as np
import copy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from OpenGL import GL
from Source.Graphics.Trackball import Trackball
from Source.Graphics.Camera import Camera
from Source.Graphics.Scene import Scene
from Source.Graphics.Gnomon import Gnomon
from Source.Graphics.World import World
from Source.Graphics.AxisMarker import AxisMarker
from Source.Graphics.WFObject import WFObject


class Renderer(QOpenGLWidget):

    # initialization
    def __init__(self, parent=None, **kwargs):
        """Initialize OpenGL version profile."""
        super(Renderer, self).__init__(parent)

        self._parent = parent
        self._edit_mode = False  # EP2
        self._edit_type = None  # EP2
        self._axis_type = None  # EP2
        self._selected_obj = None  # EP2
        self._shift_key_pressed = False  # EP2
        self.setFocusPolicy(Qt.StrongFocus)  # EP2
        self._axis_marker = None  # EP2

        # deal with options
        self._lighting = kwargs.get("lighting", True)
        self._antialiasing = kwargs.get("antialiasing", False)
        self._statistics = kwargs.get("statistics", True)

        # define home orientation
        self._home_rotation = QQuaternion.fromAxisAndAngle(QVector3D(
            1.0, 0.0, 0.0), 25.0) * QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), -50.0)

        # define scene trackball
        self._trackball = Trackball(velocity=0.05, axis=QVector3D(
            0.0, 1.0, 0.0), mode=Trackball.TrackballMode.Planar, rotation=self._home_rotation, paused=True)

        # create main scene
        self._world = World(self, home_position=QVector3D(0, 0, 3.5))

        # do not animate
        self._animating = True

        # not yet initialized
        self._initialized = False

        self.setAutoFillBackground(False)

    def printOpenGLInformation(self, format, verbosity=0):
        print("\n*** OpenGL context information ***")
        print("Vendor: {}".format(GL.glGetString(GL.GL_VENDOR).decode('UTF-8')))
        print("Renderer: {}".format(GL.glGetString(GL.GL_RENDERER).decode('UTF-8')))
        print("OpenGL version: {}".format(
            GL.glGetString(GL.GL_VERSION).decode('UTF-8')))
        print("Shader version: {}".format(GL.glGetString(
            GL.GL_SHADING_LANGUAGE_VERSION).decode('UTF-8')))
        print("Maximum samples: {}".format(GL.glGetInteger(GL.GL_MAX_SAMPLES)))
        print("\n*** QSurfaceFormat from context ***")
        print("Depth buffer size: {}".format(format.depthBufferSize()))
        print("Stencil buffer size: {}".format(format.stencilBufferSize()))
        print("Samples: {}".format(format.samples()))
        print("Red buffer size: {}".format(format.redBufferSize()))
        print("Green buffer size: {}".format(format.greenBufferSize()))
        print("Blue buffer size: {}".format(format.blueBufferSize()))
        print("Alpha buffer size: {}".format(format.alphaBufferSize()))
        #print("\nAvailable extensions:")
        # for k in range(0, GL.glGetIntegerv(GL.GL_NUM_EXTENSIONS)-1):
        #    print("{},".format(GL.glGetStringi(GL.GL_EXTENSIONS, k).decode('UTF-8')))
        #print("{}".format(GL.glGetStringi(GL.GL_EXTENSIONS, k+1).decode('UTF-8')))

    def initializeGL(self):
        """Apply OpenGL version profile and initialize OpenGL functions."""
        if not self._initialized:
            self.printOpenGLInformation(self.context().format())

            # create gnomon
            self._gnomon = Gnomon(self)

            # update cameras
            self._world.camera.setRotation(
                self._trackball.rotation().inverted())
            self._gnomon.camera.setRotation(
                self._trackball.rotation().inverted())

            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glEnable(GL.GL_DEPTH_CLAMP)
            # GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_MULTISAMPLE)
            GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)

            # attempt at line antialising
            if self._antialiasing:

                GL.glEnable(GL.GL_POLYGON_SMOOTH)
                GL.glEnable(GL.GL_BLEND)

                GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
                GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
                GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

                GL.glPointSize(5)
                GL.glLineWidth(1)

            # clear color
            GL.glClearColor(0.75, 0.76, 0.76, 0.0)

            # initialize scene
            self._world.initialize()

            # initialize gnomon
            self._gnomon.initialize()

            # timer for immediate update
            self._timer = QTimer(self)
            self._timer.setTimerType(Qt.PreciseTimer)
            self._timer.timeout.connect(self.updateScene)
            self._timer.start()

            # timer for measuring elapsed time
            self._elapsed_timer = QElapsedTimer()
            self._elapsed_timer.restart()
            self._frameElapsed = 0
            self._gpuElapsed = 0

            self._initialized = True

            ###
            # Add an object to the scene
            ###
            self._axis_marker = AxisMarker(self._world)
            self._world.addSystemActor(self._axis_marker)
        else:

            # initialize scene
            self._world.initialize()

            # initialize gnomon
            self._gnomon.initialize()

        # initialize OpenGL timer
        self._query = GL.glGenQueries(1)

    def clear(self):
        """Clear scene"""
        self._world.clear()
        self.update()

    def renderTimeEstimates(self):
        return [self._frameElapsed, self._gpuElapsed]

    @property
    def lighting(self):
        return self._lighting

    def setDrawStyle(self, style):
        self._draw_style = style

    def activeSceneCamera(self):
        """Returns main scene camera"""
        return self._world.camera

    def setAnimating(self, value):
        """Sets continuous update"""
        self._animating = value

    def isAnimating(self):
        """Returns whether continous update is active"""
        return self._animating

    def updateScene(self):
        """Schedule an update to the scene"""
        if self.isAnimating():
            self.update()

    def renderScene(self):
        """Draw main scene"""

        # set scene rotation
        self._world.camera.setRotation(self._trackball.rotation().inverted())
        self._gnomon.camera.setRotation(self._trackball.rotation().inverted())

        self._world.render()

        # render gnomon
        self._gnomon.render()

    def paintGL(self):
        """Draw scene"""

        # record render time statistics
        if self._statistics:

            # begin GPU time query
            GL.glBeginQuery(GL.GL_TIME_ELAPSED, self._query)

            # render scene
            self.renderScene()

            # finish GPU time query
            GL.glEndQuery(GL.GL_TIME_ELAPSED)

            # record render time statistics, need to stall the CPU a bit
            ready = False
            while not ready:
                ready = GL.glGetQueryObjectiv(
                    self._query, GL.GL_QUERY_RESULT_AVAILABLE)
            self._gpuElapsed = GL.glGetQueryObjectuiv(
                self._query, GL.GL_QUERY_RESULT) / 1000000.0

            # delete query object
            #GL.glDeleteQueries( self._query )

        else:

            # render scene
            self.renderScene()

        self._frameElapsed = self._elapsed_timer.restart()

    def resizeGL(self, width, height):
        """ Called by the Qt libraries whenever the window is resized"""
        self._world.camera.setAspectRatio(
            width / float(height if height > 0.0 else 1.0))

    def pan(self, point, state='start'):
        """Move camera according to mouse move"""
        if state == 'start':
            self._lastPanningPos = point
        elif state == 'move':
            delta = QLineF(self._lastPanningPos, point)
            self._lastPanningPos = point
            direction = QVector3D(-delta.dx(), -delta.dy(), 0.0).normalized()
            newpos = self._world.camera.position + delta.length()*2.0 * direction
            self._world.camera.setPosition(newpos)

    def mousePressEvent(self, event):
        """ Called by the Qt libraries whenever the window receives a mouse click."""
        super(Renderer, self).mousePressEvent(event)

        if event.isAccepted():
            return

        if event.buttons() & Qt.LeftButton:

            near_object = self._get_near_obj(event)
            if near_object:
                if self._shift_key_pressed:
                    self._select_object(near_object)
                if self._edit_mode:
                    self._edit_mode_press(event)
            else:
                self._exit_edit_mode()

            if not self._edit_mode:
                self._trackball.press(self._pixelPosToViewPos(
                    event.localPos()), QQuaternion())
                self._trackball.start()
                event.accept()
                if not self.isAnimating():
                    self.update()

        elif event.buttons() & Qt.RightButton:
            self.pan(self._pixelPosToViewPos(event.localPos()), state='start')
            self.update()

    def mouseMoveEvent(self, event):
        """Called by the Qt libraries whenever the window receives a mouse move/drag event."""
        super(Renderer, self).mouseMoveEvent(event)

        if event.isAccepted():
            return

        if event.buttons() & Qt.LeftButton:

            if not self._edit_mode:
                self._trackball.move(self._pixelPosToViewPos(
                    event.localPos()), QQuaternion())
                event.accept()
                if not self.isAnimating():
                    self.update()
            else:
                self._edit_mode_move(event)  # EP2

        elif event.buttons() & Qt.RightButton:
            self.pan(self._pixelPosToViewPos(event.localPos()), state='move')
            self.update()

    def mouseReleaseEvent(self, event):
        """ Called by the Qt libraries whenever the window receives a mouse release."""
        super(Renderer, self).mouseReleaseEvent(event)

        if event.isAccepted():
            return

        if event.button() == Qt.LeftButton:
            self._trackball.release(self._pixelPosToViewPos(
                event.localPos()), QQuaternion())
            event.accept()
            if not self.isAnimating():
                self._trackball.stop()
                self.update()

    def wheelEvent(self, event):
        """Process mouse wheel movements"""
        super(Renderer, self).wheelEvent(event)
        self.zoom(-event.angleDelta().y() / 950.0)
        event.accept()
        # scene is dirty, please update
        self.update()

    def zoom(self, diffvalue):
        """Zooms in/out the active camera"""
        multiplicator = math.exp(diffvalue)

        # get a hold of the current active camera
        camera = self._world.camera

        if camera.lens == Camera.Lens.Orthographic:
            # Since there's no perspective, "zooming" in the original sense
            # of the word won't have any visible effect. So we just increase
            # or decrease the field-of-view values of the camera instead, to
            # "shrink" the projection size of the model / scene.
            camera.scaleHeight(multiplicator)
        else:
            old_focal_dist = camera.focalDistance
            new_focal_dist = old_focal_dist * multiplicator

            direction = camera.orientation * QVector3D(0.0, 0.0, -1.0)
            newpos = camera.position + \
                (new_focal_dist - old_focal_dist) * -direction

            camera.setPosition(newpos)
            camera.setFocalDistance(new_focal_dist)

    def viewFront(self):
        """Make camera face the front side of the scene"""
        self._trackball.reset(QQuaternion())
        self.update()

    def viewBack(self):
        """Make camera face the back side of the scene"""
        self._trackball.reset(QQuaternion.fromAxisAndAngle(
            QVector3D(0.0, 1.0, 0.0), 180.0))
        self.update()

    def viewLeft(self):
        """Make camera face the left side of the scene"""
        self._trackball.reset(QQuaternion.fromAxisAndAngle(
            QVector3D(0.0, 1.0, 0.0), -90.0))
        self.update()

    def viewRight(self):
        """Make camera face the right side of the scene"""
        self._trackball.reset(QQuaternion.fromAxisAndAngle(
            QVector3D(0.0, 1.0, 0.0), 90.0))
        self.update()

    def viewTop(self):
        """Make camera face the top side of the scene"""
        self._trackball.reset(QQuaternion.fromAxisAndAngle(
            QVector3D(1.0, 0.0, 0.0), 90.0))
        self.update()

    def viewBottom(self):
        """Make camera face the bottom side of the scene"""
        self._trackball.reset(QQuaternion.fromAxisAndAngle(
            QVector3D(1.0, 0.0, 0.0), -90.0))
        self.update()

    def createGridLines(self):
        """Set gridlines"""
        self.makeCurrent()
        self._world.createGridLines()
        self.doneCurrent()

    def cameraLensChanged(self, lens):
        """Switch world's. camera lens"""
        self._world.setCameraLens(lens)
        self._gnomon.setCameraLens(lens)
        self.update()

    def storeCamera(self):
        """Store world's camera parameters"""
        self._world.storeCamera()

    def recallCamera(self):
        """Recall camera parameters"""
        self._world.recallCamera()
        self._trackball.reset(self._world.camera.rotation.inverted())
        self.update()

    def resetCamera(self):
        """Reset world's camera parameters"""
        self._world.resetCamera()
        self._trackball.reset(self._home_rotation)
        self.update()

    def drawStyleChanged(self, index):
        self._world.setDrawStyle(Scene.DrawStyle.Styles[index])
        self.update()

    def lightingChanged(self, state):
        self._world.setLighting(state)
        self.update()

    def shadingChanged(self, index):
        self._world.setShading(Scene.Shading.Types[index])
        self.update()

    def headLightChanged(self, state):
        self._world.light.setHeadLight(state)
        self.update()

    def directionalLightChanged(self, state):
        self._world.light.setDirectional(state)
        self.update()

    def enableProfiling(self, enable):
        self._statistics = enable

    def enableAnimation(self, enable):
        self.setAnimating(enable)
        if not enable:
            self._trackball.stop()

    def _pixelPosToViewPos(self, point):
        return QPointF(2.0 * float(point.x()) / self.width() - 1.0, 1.0 - 2.0 * float(point.y()) / self.height())

    #######################################
    # Métodos implementados para este EP2 #
    #######################################

    # EP2
    def add_object(self):
        """Adiciona um objeto à cena"""
        filename, filetype = QFileDialog.getOpenFileName(
            self, 'Open file', filter='WaveFront Object (*.obj)', options=QFileDialog.DontUseNativeDialog)
        if filename:
            self.makeCurrent()
            self._world.addActor(WFObject(self._world, filename=filename))
            self.doneCurrent()
            self.setFocus()

    # EP2
    def _get_near_obj(self, event):
        """Retorna o objeto mais próximo apontado pelo mouse"""
        point = self._pixelPosToViewPos(event.localPos())
        ray = self._world.ray(point)
        selected_objs = {}
        for actor in self._world.actors():
            result, t = actor.intersect(ray)
            if result:
                selected_objs[t] = actor
        if selected_objs:
            near = sorted(selected_objs.keys())[0]
            return selected_objs[near]
        else:
            return None

    # EP2
    def _select_object(self, near_object):
        """Procedimentos na escolha do objeto"""
        self._exit_edit_mode()
        self._selected_obj = near_object
        self._selected_obj.setHighlighted(True)
        self._axis_marker.setTransform(self._selected_obj.transform())
        self._edit_mode = True

    # EP2
    def _exit_edit_mode(self):
        """Procedimentos na saída do modo de edição"""
        for obj in self._world.actors():
            obj.setHighlighted(False)
        self._selected_obj = None
        self._edit_mode = False
        self._edit_type = None
        self._axis_type = None
        self._start_obj_xform = None
        self._start_obj_pos = None
        self._axis_marker.reset_visibility()
        self._axis_marker.reset_highlight()

    # EP2
    def _edit_mode_press(self, event):
        """Inicia o processo de captura do movimento do mouse de acordo com a opção da transformação"""
        if self._edit_type == 'R':
            self.obj_trackball(event, state='start')
            self._start_obj_quat = self._obj_trackball.rotation()
        else:
            self.slider(event, state='start')
            self._start_obj_pos = self._selected_obj.position()
        self._start_obj_xform = copy.deepcopy(self._selected_obj.transform())

    # EP2
    def _edit_mode_move(self, event):
        """Aplica as transformações no objeto selecionado de acordo com o tipo da transformação e movimento do mouse"""
        if self._edit_type == 'T':
            self._edit_type_translate(event)
        elif self._edit_type == 'R':
            self._edit_type_rotate(event)
        elif self._edit_type == 'S':
            self._edit_type_scale(event)

    # EP2
    def _edit_type_translate(self, event):
        """Aplica a operação de translação ao objeto selecionado de acordo com o movimento do mouse"""
        delta = self.slider(event, state='move') * 10
        xform = self._selected_obj.transform()
        if self._axis_type == 'X':
            xform[0, 3] += delta
        elif self._axis_type == 'Y':
            xform[1, 3] += delta
        elif self._axis_type == 'Z':
            xform[2, 3] += delta
        self._axis_marker.update('translate')

    # EP2
    def _edit_type_rotate(self, event):
        """Aplica a operação de rotação ao objeto selecionado de acordo com o movimento do mouse"""
        quat = self.obj_trackball(event, state='move')
        xform = self._selected_obj.transform()
        xform.rotate(quat)
        self._axis_marker.update('rotate')

    # EP2
    def _edit_type_scale(self, event):
        """Aplica a operação de escala ao objeto selecionado de acordo com o movimento do mouse"""
        delta = self.slider(event, state='move') + 1
        xform = self._selected_obj.transform()
        if self._axis_type == 'X':
            xform.scale(delta, 1, 1)
        elif self._axis_type == 'Y':
            xform.scale(1, delta, 1)
        elif self._axis_type == 'Z':
            xform.scale(1, 1, delta)
        elif self._axis_type == 'W':
            xform.scale(delta, delta, delta)
        self._axis_marker.update('scale')

    # EP2
    def keyPressEvent(self, event):
        super(Renderer, self).keyPressEvent(event)

        if event.isAccepted():
            return

        if event.key() == Qt.Key_Shift:
            self._shift_key_pressed = True

        if self._edit_mode:

            if event.key() == Qt.Key_Delete or event.key() == Qt.Key_X and not self._edit_type:
                self._world.removeActor(self._selected_obj)
                self._exit_edit_mode()
            elif event.key() == Qt.Key_T:
                self._edit_type = 'T'
                self._axis_marker.set_translate()
            elif event.key() == Qt.Key_R:
                self._edit_type = 'R'
                self._axis_marker.set_rotate()
            elif event.key() == Qt.Key_S:
                self._edit_type = 'S'
                self._axis_marker.set_scale()
            elif event.key() == Qt.Key_X:
                self._axis_type = 'X'
                self._axis_marker.set_axis('X')
            elif event.key() == Qt.Key_Y:
                self._axis_type = 'Y'
                self._axis_marker.set_axis('Y')
            elif event.key() == Qt.Key_Z:
                self._axis_type = 'Z'
                self._axis_marker.set_axis('Z')
            elif event.key() == Qt.Key_W:
                self._axis_type = 'W'
                self._axis_marker.set_axis('W')
            elif event.key() == Qt.Key_Escape:
                self._selected_obj.setTransform(self._start_obj_xform)
                self._exit_edit_mode()

    # EP2
    def keyReleaseEvent(self, event):
        super(Renderer, self).keyReleaseEvent(event)

        if event.isAccepted():
            return

        if event.key() == Qt.Key_Shift:
            self._shift_key_pressed = False

    # EP2
    def slider(self, event, state='start'):
        """Slider virtual"""
        point = self._pixelPosToViewPos(event.localPos())
        if state == 'start':
            self._last_slider_pos = point
        elif state == 'move':
            delta = point.x() - self._last_slider_pos.x()
            self._last_slider_pos = point
            return delta

    # EP2
    def obj_trackball(self, event, state='start'):
        """Trackball virtual"""
        point = self._pixelPosToViewPos(event.localPos()) / 10
        if state == 'start':
            self._obj_trackball = Trackball(mode=Trackball.TrackballMode.Planar, paused=True)
            self._obj_trackball.press(point, QQuaternion())
            self._obj_trackball.start()
        elif state == 'move':
            self._obj_trackball.move(point, QQuaternion())
            return self._obj_trackball.rotation()
        else:
            self._obj_trackball.release(point, QQuaternion())
            return self._obj_trackball.rotation()
