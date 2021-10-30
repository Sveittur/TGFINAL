try:
    try:
        from OpenGL.GL import * # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        print('Drat, patching for Big Sur')
        from ctypes import util
        orig_util_find_library = util.find_library
        def new_util_find_library( name ):
            res = orig_util_find_library( name )
            if res: return res
            return '/System/Library/Frameworks/'+name+'.framework/'+name
        util.find_library = new_util_find_library
        from OpenGL.GL import *
except ImportError:
    pass

import OpenGL.GLU

from math import * # trigonometry

import sys

from Objects import *

class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader,shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader,shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        self.positionLoc			= glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)


        self.normalLoc			= glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        self.uvLoc			= glGetAttribLocation(self.renderingProgramID, "a_uv")
        glEnableVertexAttribArray(self.uvLoc)

        self.modelMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_model_matrix")
        self.ViewMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_view_matrix")
        self.projectionMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")
        
        self.eyePosLoc			= glGetUniformLocation(self.renderingProgramID, "u_eye_position")

        self.materialDiffuseLoc			= glGetUniformLocation(self.renderingProgramID, "u_mat_diffuse")
        self.materialSpecularLoc			= glGetUniformLocation(self.renderingProgramID, "u_mat_specular")
        self.materialShininessLoc			= glGetUniformLocation(self.renderingProgramID, "u_mat_shininess")

        self.diffuseTextureLoc			= glGetUniformLocation(self.renderingProgramID, "u_tex01")
        self.usingTextureLoc                 = glGetUniformLocation(self.renderingProgramID, "u_using_texture")
        self.specularTextureLoc			= glGetUniformLocation(self.renderingProgramID, "u_tex02")

        self.globalLightDirectionLoc    = glGetUniformLocation(self.renderingProgramID, "u_global_light_direction")
        self.globalLightDiffuseLoc = glGetUniformLocation(self.renderingProgramID, "u_global_light_color")
        self.globalLightDirectionLoc2    = glGetUniformLocation(self.renderingProgramID, "u_global_light_direction2")
        self.globalLightDiffuseLoc2 = glGetUniformLocation(self.renderingProgramID, "u_global_light_color2")

        
    
    def use(self):
        try:
            glUseProgram(self.renderingProgramID)   
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.ViewMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_uv_attribute(self, vertex_array):
        glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 0, vertex_array)

    def set_eye_position(self, pos):
        glUniform4f(self.eyePosLoc, pos.x, pos.y, pos.z, 1.0)

    def set_material_diffuse(self,color):
        glUniform4f(self.materialDiffuseLoc, color.r, color.g, color.b, 1.0)
    
    def set_material_specular(self,color):
        glUniform4f(self.materialSpecularLoc, color.r, color.g, color.b, 1.0)

    def set_material_shininess(self,shininess):
        glUniform1f(self.materialShininessLoc, shininess)

    def set_diffuse_texture(self,number):
        glUniform1i(self.diffuseTextureLoc,number)

    def set_using_texture(self):
        glUniform1f(self.usingTextureLoc,GL_TRUE)
    
    def set_not_using_texture(self):
        glUniform1f(self.usingTextureLoc,GL_FALSE)

    def set_spec_texture(self,number):
        glUniform1i(self.specularTextureLoc,number)

    def set_global_light_direction(self, pos):
        glUniform4f(self.globalLightDirectionLoc, pos.x, pos.y, pos.z, 1.0)

    def set_global_light_diffuse(self, rgb):
        glUniform4f(self.globalLightDiffuseLoc, rgb.r, rgb.g, rgb.b, 1.0)

    def set_global_light_direction2(self, pos):
        glUniform4f(self.globalLightDirectionLoc2, pos.x, pos.y, pos.z, 1.0)

    def set_global_light_diffuse2(self, rgb):
        glUniform4f(self.globalLightDiffuseLoc2, rgb.r, rgb.g, rgb.b, 1.0)

    def set_attribute_buffers(self, vertex_buffer_id, has_texture=0):
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        if(has_texture == 1.0):
            glUniform1f(self.usingTextureLoc, GL_TRUE)
            glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(0))
            glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)))
            glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(6 * sizeof(GLfloat)))
        else:
            glUniform1f(self.usingTextureLoc,GL_FALSE)
            glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(0))
            glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)))