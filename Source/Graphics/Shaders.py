from PyQt5.QtCore import QObject
from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram

## singleton shader class 
class Shaders(QObject):

	__instance = None

	def __new__(cls):
		if Shaders.__instance is None:
			Shaders.__instance = QObject.__new__(cls)
			Shaders.__instance.initialize()
		return Shaders.__instance


	def initialize(self):
		"""Create shader programs"""

		## create background shader program
		self.__instance._backgroundShader = QOpenGLShaderProgram()
		self.__instance._backgroundShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.attributeColorNoTransformVertexShader())
		self.__instance._backgroundShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.simpleFragmentShader())
		self.__instance._backgroundShader.link()

		## create uniform material shader with no lighting 
		self.__instance._wireframeMaterialShader = QOpenGLShaderProgram()
		self.__instance._wireframeMaterialShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.wireframeMaterialVertexShader())
		self.__instance._wireframeMaterialShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.simpleFragmentShader())
		self.__instance._wireframeMaterialShader.link()

		## create uniform material shader with no lighting 
		self.__instance._uniformMaterialShader = QOpenGLShaderProgram()
		self.__instance._uniformMaterialShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.uniformMaterialVertexShader())
		self.__instance._uniformMaterialShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.simpleFragmentShader())
		self.__instance._uniformMaterialShader.link()

		## create uniform material with no lighting calculations
		self.__instance._attributeColorShader = QOpenGLShaderProgram()
		self.__instance._attributeColorShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.attributeColorTransformVertexShader())
		self.__instance._attributeColorShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.simpleFragmentShader())
		self.__instance._attributeColorShader.link()

		## create Phong mesh shader
		self.__instance._uniformMaterialPhongShader = QOpenGLShaderProgram()
		self.__instance._uniformMaterialPhongShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.uniformMaterialPhongVertexShader())
		self.__instance._uniformMaterialPhongShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.uniformMaterialPhongFragmentShader())
		self.__instance._uniformMaterialPhongShader.link()

		## create color-based Phong mesh shader
		self.__instance._attributeColorPhongShader = QOpenGLShaderProgram()
		self.__instance._attributeColorPhongShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.attributeMaterialPhongVertexShader())
		self.__instance._attributeColorPhongShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.attributeMaterialPhongFragmentShader())
		self.__instance._attributeColorPhongShader.link()

		## create Phong mesh shader
		self.__instance._uniformMaterialPhongFlatShader = QOpenGLShaderProgram()
		self.__instance._uniformMaterialPhongFlatShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.uniformMaterialPhongVertexFlatShader())
		self.__instance._uniformMaterialPhongFlatShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.uniformMaterialPhongFragmentFlatShader())
		self.__instance._uniformMaterialPhongFlatShader.link()

		## create color-based Phong mesh shader
		self.__instance._attributeColorPhongFlatShader = QOpenGLShaderProgram()
		self.__instance._attributeColorPhongFlatShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.attributeMaterialPhongVertexFlatShader())
		self.__instance._attributeColorPhongFlatShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.attributeMaterialPhongFragmentFlatShader())
		self.__instance._attributeColorPhongFlatShader.link()

		## create simple textured-based mesh shader
		self.__instance._texturedShader = QOpenGLShaderProgram()
		self.__instance._texturedShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.texturedVertexShader())
		self.__instance._texturedShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.texturedFragmentShader())
		self.__instance._texturedShader.link()	

		## create simple textured-based mesh flat shader
		self.__instance._texturedFlatShader = QOpenGLShaderProgram()
		self.__instance._texturedFlatShader.addShaderFromSourceCode(QOpenGLShader.Vertex, Shaders.texturedVertexFlatShader())
		self.__instance._texturedFlatShader.addShaderFromSourceCode(QOpenGLShader.Fragment, Shaders.texturedFragmentFlatShader())
		self.__instance._texturedFlatShader.link()	


	@classmethod
	def uniformMaterialPhongVertexFlatShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		flat out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def uniformMaterialPhongFragmentFlatShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		flat in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;

		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * material.diffuse * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			fragColor = vec4(intensity, 1.0);
		}
		"""
		return fragmentShaderSource


	@classmethod
	def attributeMaterialPhongVertexFlatShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		layout(location = 2) in vec3 color;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		flat out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;
		smooth out vec3 vertexColor;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    vertexColor = color;
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def attributeMaterialPhongFragmentFlatShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		flat in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;
		smooth in vec3 vertexColor;

		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * vertexColor * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			fragColor = vec4(intensity, 1.0);
		}
		"""
		return fragmentShaderSource
		

	@classmethod
	def uniformMaterialPhongVertexShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		smooth out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def uniformMaterialPhongFragmentShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		smooth in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;

		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * material.diffuse * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			fragColor = vec4(intensity, 1.0);
		}
		"""
		return fragmentShaderSource


	@classmethod
	def attributeMaterialPhongVertexShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		layout(location = 2) in vec3 color;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		smooth out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;
		smooth out vec3 vertexColor;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    vertexColor = color;
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def attributeMaterialPhongFragmentShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		smooth in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;
		smooth in vec3 vertexColor;

		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * vertexColor * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			fragColor = vec4(intensity, 1.0);
		}
		"""
		return fragmentShaderSource


	@classmethod
	def attributeColorNoTransformVertexShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 2) in vec3 color;
		smooth out vec4 vertexColor;

		void main()
		{
			gl_Position = vec4(position, 1.0);
			vertexColor = vec4(color, 1.0);
		}
		"""
		return vertexShaderSource


	@classmethod
	def uniformMaterialVertexShader(cls):
		vertexShaderSource = """
		#version 400
		
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		layout(location = 0) in vec3 position;
		
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform Material material;

		smooth out vec4 vertexColor;

		void main()
		{
		    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexColor = vec4(material.diffuse, 1.0);
		}
		"""
		return vertexShaderSource


	@classmethod
	def texturedVertexShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		layout(location = 2) in vec3 color;
		layout(location = 3) in vec2 texcoord;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		smooth out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;
		smooth out vec2 textureCoord;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    textureCoord = texcoord;
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def texturedVertexFlatShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 1) in vec3 normal;
		layout(location = 2) in vec3 color;
		layout(location = 3) in vec2 texcoord;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform mat3 normalMatrix;
		uniform vec4 lightPosition;
		uniform vec3 lightAttenuation;

		flat out vec4 vertexNormal;
		smooth out vec4 vertexPosition;
		smooth out vec3 lightDirection;
		smooth out float attenuation;
		smooth out vec2 textureCoord;

		void main()
		{
		    vertexPosition = viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexNormal = viewMatrix * vec4(normalMatrix * normal, 0.0);
		    if (lightPosition.w == 0.0) {
				lightDirection = normalize(lightPosition.xyz);
				attenuation = 1.0;
			} else {
		    	lightDirection = normalize(lightPosition.xyz - vertexPosition.xyz);
		    	float distance = length(lightPosition.xyz - vertexPosition.xyz);
		    	attenuation = 1.0 / (lightAttenuation.x + lightAttenuation.y * distance + lightAttenuation.z * distance * distance);
		    }
		    textureCoord = texcoord;
		    gl_Position = projectionMatrix * vertexPosition;
		}
		"""
		return vertexShaderSource


	@classmethod
	def wireframeMaterialVertexShader(cls):
		vertexShaderSource = """
		#version 400
		
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		layout(location = 0) in vec3 position;
		
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		uniform Material wireframe_material;

		smooth out vec4 vertexColor;

		void main()
		{
		    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexColor = vec4(wireframe_material.diffuse, 1.0);
		}
		"""
		return vertexShaderSource


	@classmethod
	def attributeColorTransformVertexShader(cls):
		vertexShaderSource = """
		#version 400
		layout(location = 0) in vec3 position;
		layout(location = 2) in vec3 color;
		uniform mat4 modelMatrix;
		uniform mat4 viewMatrix;
		uniform mat4 projectionMatrix;
		smooth out vec4 vertexColor;

		void main()
		{
		    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
		    vertexColor = vec4(color, 1.0);
		}
		"""
		return vertexShaderSource


	@classmethod
	def simpleFragmentShader(cls):
		fragmentShaderSource = """
		#version 400
		smooth in vec4 vertexColor;
		out vec4 fragColor;

		void main()
		{
			fragColor = vertexColor;
		}
		"""
		return fragmentShaderSource


	@classmethod
	def texturedFragmentShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		smooth in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;
		smooth in vec2 textureCoord;

		uniform float selected;
		uniform sampler2D texObject;
		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * material.diffuse * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			vec4 tex = texture(texObject, textureCoord.st);
			fragColor = (1.0 - tex.a) * vec4(intensity, 1.0) + tex.a * vec4(selected * tex.rgb, 1.0);
		}
		"""
		return fragmentShaderSource


	@classmethod
	def texturedFragmentFlatShader(cls):
		fragmentShaderSource = """
		#version 400
		struct Material {
			vec3 emission;
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;    
			float shininess;
		}; 

		struct Light {
			vec3 ambient;
			vec3 diffuse;
			vec3 specular;
		};

		flat in vec4 vertexNormal;
		smooth in vec4 vertexPosition;
		smooth in vec3 lightDirection;
		smooth in float attenuation;
		smooth in vec2 textureCoord;

		uniform float selected;
		uniform sampler2D texObject;
		uniform Material material;
		uniform Light light;

		out vec4 fragColor;

		void main()
		{
			// ambient term
			vec3 ambient = material.ambient * light.ambient;

			// diffuse term
			vec3 N = normalize(vertexNormal.xyz);
			vec3 L = normalize(lightDirection);
			vec3 diffuse = light.diffuse * material.diffuse * max(dot(N, L), 0.0);

			// specular term
			vec3 E = normalize(-vertexPosition.xyz);
	 		vec3 R = normalize(-reflect(L, N)); 
			vec3 specular = light.specular * material.specular * pow(max(dot(R, E), 0.0), material.shininess);

			// final intensity
			vec3 intensity = material.emission + clamp(ambient + attenuation * (diffuse + specular), 0.0, 1.0);
			vec4 tex = texture(texObject, textureCoord.st);
			fragColor = (1.0 - tex.a) * vec4(intensity, 1.0) + tex.a * vec4(selected * tex.rgb, 1.0);
		}
		"""
		return fragmentShaderSource


	def backgroundShader(self):
		return self.__instance._backgroundShader


	def uniformMaterialShader(self):
		return self.__instance._uniformMaterialShader


	def wireframeMaterialShader(self):
		return self.__instance._wireframeMaterialShader


	def attributeColorShader(self):
		return self.__instance._attributeColorShader
		

	def uniformMaterialPhongShader(self):
		return self.__instance._uniformMaterialPhongShader


	def attributeColorPhongShader(self):
		return self.__instance._attributeColorPhongShader


	def uniformMaterialPhongFlatShader(self):
		return self.__instance._uniformMaterialPhongFlatShader


	def attributeColorPhongFlatShader(self):
		return self.__instance._attributeColorPhongFlatShader
		

	def texturedShader(self):
		return self.__instance._texturedShader


	def texturedFlatShader(self):
		return self.__instance._texturedFlatShader


