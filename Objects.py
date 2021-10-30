from os import X_OK
import random
from random import *
from sys import _xoptions
import numpy as np
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

from OpenGL.GLU import *

import math
from math import *


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        length = self.__len__()
        self.x /= length
        self.y /= length
        self.z /= length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)

class Cube:
    def __init__(self):
        self.position_array = [-0.5, -0.5, -0.5,
                            -0.5, 0.5, -0.5,
                            0.5, 0.5, -0.5,
                            0.5, -0.5, -0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            0.5, 0.5, 0.5,
                            0.5, -0.5, 0.5,
                            -0.5, -0.5, -0.5,
                            0.5, -0.5, -0.5,
                            0.5, -0.5, 0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, -0.5,
                            0.5, 0.5, -0.5,
                            0.5, 0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            -0.5, -0.5, -0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            -0.5, 0.5, -0.5,
                            0.5, -0.5, -0.5,
                            0.5, -0.5, 0.5,
                            0.5, 0.5, 0.5,
                            0.5, 0.5, -0.5]

        self.normal_array = [0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0]

        self.uv_array = [   
                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0,

                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0,

                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0,

                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0,

                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0,

                            0.0, 0.0, 
                            0.0, 1.0, 
                            1.0, 1.0, 
                            1.0, 0.0
                             ]

    def set_verticies(self,shader):
        shader.set_position_attribute(self.position_array)
        shader.set_normal_attribute(self.normal_array)
        shader.set_uv_attribute(self.uv_array)

    def draw(self, shader):
        shader.set_position_attribute(self.position_array)
        shader.set_normal_attribute(self.normal_array)
        shader.set_uv_attribute(self.uv_array)
        
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 4, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 8, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 12, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 16, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 20, 4)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class Material:
    def __init__(self, diffuse = None, specular = None, shininess = None):
        self.diffuse = Color(0.0, 0.0, 0.0) if diffuse is None else diffuse
        self.specular = Color(0.0, 0.0, 0.0) if specular is None else specular
        self.shininess = 1 if shininess is None else shininess
    
        
        

        

class MeshModel:
    def __init__(self):
        self.vertex_arrays = dict()
        # self.index_arrays = dict()
        self.mesh_materials = dict()
        self.materials = dict()
        self.vertex_counts = dict()
        self.vertex_buffer_ids = dict()

    def add_vertex(self, mesh_id, position, normal,uv):
        if mesh_id not in self.vertex_arrays:
            self.vertex_arrays[mesh_id] = []
            self.vertex_counts[mesh_id] = 0
        if uv == 1:
            self.vertex_arrays[mesh_id] += [position.x, position.y, position.z, normal.x, normal.y, normal.z]
        else:
            self.vertex_arrays[mesh_id] += [position.x, position.y, position.z, normal.x, normal.y, normal.z,uv.x,uv.y]
        self.vertex_counts[mesh_id] += 1

    def set_mesh_material(self, mesh_id, mat_id):
        self.mesh_materials[mesh_id] = mat_id

    def add_material(self, mat_id, mat):
        self.materials[mat_id] = mat

    def set_opengl_buffers(self):
        for mesh_id in self.mesh_materials.keys():
            self.vertex_buffer_ids[mesh_id] = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_ids[mesh_id])
            glBufferData(GL_ARRAY_BUFFER, np.array(self.vertex_arrays[mesh_id], dtype='float32'), GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
    


    def draw(self, shader, using_uv = False):
        for mesh_id, mesh_material in self.mesh_materials.items():
            material = self.materials[mesh_material]
            shader.set_material_specular(material.specular)
            shader.set_material_shininess(material.shininess)
            shader.set_material_diffuse(material.diffuse)
            shader.set_attribute_buffers(self.vertex_buffer_ids[mesh_id])
            if using_uv:
                shader.set_attribute_buffers(self.vertex_buffer_ids[mesh_id], 1.0)
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_counts[mesh_id])
            glBindBuffer(GL_ARRAY_BUFFER, 0)

class GameObject():
    def __init__(self, position,scale , vector = None):
        self.position = position
        self.scale = scale
        self.minX = self.position.x - scale.x/2
        self.maxX = self.position.x + scale.x/2
        self.minZ = self.position.z - scale.z/2
        self.maxZ = self.position.z + scale.z/2
        self.vector = vector

    def update(self, newPos):
        self.position = newPos
        self.minX = self.position.x - self.scale.x/2
        self.maxX = self.position.x + self.scale.x/2
        self.minZ = self.position.z - self.scale.z/2
        self.maxZ = self.position.z + self.scale.z/2 
    
    def checkIntersection(self, other):
        return (self.minX <= other.maxX and self.maxX >= other.minX) and \
               (self.minZ <= other.maxZ and self.maxZ >= other.minZ)

    def doCollision(self,other):
        pass
        

    
class player():
    def __init__(self, position,scale=Point(1,1,1)):
        self.position = position
        self.scale = scale
        self.minX = self.position.x - scale.x/2
        self.maxX = self.position.x + scale.x/2
        self.minZ = self.position.z - scale.z/2
        self.maxZ = self.position.z + scale.z/2
        self.radius = self.scale.x / 2
        self.velocity = 2
    
    def update(self, newPos):
        self.position = newPos
        self.minX = self.position.x - self.scale.x/2
        self.maxX = self.position.x + self.scale.x/2
        self.minZ = self.position.z - self.scale.z/2
        self.maxZ = self.position.z + self.scale.z/2

    def checkIntersection(self, other):
        x = max(other.position.x - other.scale.x / 2,
                min(self.position.x, (other.position.x + other.scale.x / 2)))
        y = max(other.position.y - other.scale.y / 2,
                min(self.position.y, (other.position.y + other.scale.y / 2)))
        z = max(other.position.z - other.scale.z / 2,
                min(self.position.z, (other.position.z + other.scale.z / 2)))

        distance_squared = (x - self.position.x) ** 2 + \
                           (y - self.position.y) ** 2 + \
                           (z - self.position.z) ** 2

        return distance_squared < (self.radius ** 2)


    def doCollision(self, other):
        # collisionSurface = "none"
        # if self.minX < other.minX:
        #     collisionSurface = "top"
        # if self.maxX > other.maxX:
        #     collisionSurface = "bottom"
        # if self.minZ < other.minZ:
        #     collisionSurface =  "right"
        # if self.maxZ > other.maxZ:
        #     collisionSurface = "left"
        # print(collisionSurface)
        # print("x ", self.position.x, "z ",self.position.z)
        # print("meMaxz ", self.maxZ, "otherMaxz ",other.maxZ)

        # if collisionSurface == "top":
        #     self.position.x = other.minX - self.scale.x / 2
        # elif collisionSurface == "bottom":
        #     self.position.x = other.maxX + self.scale.x / 2
        # elif collisionSurface == "right":
        #     self.position.z = other.minZ - self.scale.z / 2
        # elif collisionSurface == "left":
        #     self.position.z = other.maxZ + self.scale.z / 2
        tempselfx = self.position.x
        tempselfz = self.position.z
        tempotherx = other.position.x
        tempotherz = other.position.z


        if self.position.x < 0:
            tempselfx = abs(self.position.x) + 5
        if self.position.z < 0:
            tempselfz = abs(self.position.z)
        
        if other.position.x < 0:
            tempotherx = abs(other.position.x) + 5
        if self.position.z < 0:
            tempotherz = abs(other.position.z)

        w = tempotherx - tempselfx
        h = tempotherz - tempselfz
        if w >= abs(h):
            if self.position.x > 0:
                self.position.x = other.minX - self.scale.x / 2
            else:
                self.position.x = other.maxX + self.scale.x / 2
            # return True
        elif -w >= abs(h):
            if self.position.x > 0:
                self.position.x = other.maxX + self.scale.x /2
            else:
                self.position.x = other.minX - self.scale.x / 2
            # return True
        elif h >= abs(w):
            self.position.z = other.maxZ + self.scale.z / 2
            # return True
        elif -h >= abs(w):
            self.position.z = other.minZ - self.scale.z / 2

    def jumpUp(self):
        self.position.y += 0.1
    def jumpDown(self):
        self.position.y -= 0.1
