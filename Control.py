
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
from math import *
from OpenGL.GL.ARB import robust_buffer_access_behavior, viewport_array
from OpenGL.error import NullFunctionError
from OpenGL.latebind import LateBind

import pygame
from pygame.locals import *
from pygame import mixer
from pygame import time

import numpy as np

import sys
import time

from Shaders import *
from Matrices import *


import objLoader



class GraphicsProgram3D:
    def __init__(self):

        pygame.init() 
        self.width = 1280
        self.height = 600
        self.gameDisplay = pygame.display.set_mode((self.width,self.height), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(5,0.2,0), Point(0,0.2,0),Vector(0,1,0))

        self.projection_matrix = ProjectionMatrix()
        self.fov = 70*pi/180 # 80 deg
        self.projection_matrix.set_perspective(pi/2, self.width/self.height, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.init_lights()
        self.player = player(Point(0,0.2,0))
        self.wallList = []
        wallObject = GameObject(Point(3,0,-1),Point(1,1,1))
        wallObject2 = GameObject(Point(-2,0,-1),Point(1,1,1))
        wallObject3 = GameObject(Point(3,0,-3),Point(1,1,1))
        self.enemyM = GameObject(Point(2,-0.3,-3),Point(0.3,1,0.3))
        self.wallList.append(wallObject)
        self.wallList.append(wallObject2)
        self.wallList.append(wallObject3)

        self.shotlist = []


        self.cube = Cube()
        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.collisionRadius = 0.35
        self.knifeangle = 0

        self.w_key_down = False
        self.s_key_down = False
        self.a_key_down = False
        self.d_key_down = False
        self.space_key_down = False
        self.active_slot = 3
        self.jumping = False
        self.falling = False
        self.shooting = False
        self.knifing = False
        self.knifeAnimX = 0
        self.knifeAnimY = 0
        self.knifeAnimZ = 0


        self.moveVec = Vector(0,0,0)
        self.stopwatch = None

        self.lastX, self.lastY = self.width/2,self.height/2
        self.xPos, self.yPos = 0,0
        self.firstMouse = True

        
        

        #WALL TEXTURE INITIALIZATION
        self.wallTextureID = self.loadTexture('texture/walls.jpeg')
        self.playerTextureID = self.loadTexture('texture/HuManDefuse.png')
        self.karambitTextureID = self.loadTexture('texture/Karambit.png')
        self.rifleTextureID = self.loadTexture('texture/ak.bmp')
        self.earthTextureID = self.loadTexture('texture/Earth_Diffuse_6K.jpg')
        self.saturnTextureID = self.loadTexture('texture/saturn.jpg')


        # OBJECTS
        self.knife = objLoader.load_obj_file('objects','throwingknife.obj')
        self.pistol = objLoader.load_obj_file('objects','M9.obj')
        self.rifle = objLoader.load_obj_file('objects','ak.obj')
        self.enemy = objLoader.load_obj_file('objects','human.obj')
        self.sus = objLoader.load_obj_file('objects','sus.obj')
        self.karambit = objLoader.load_obj_file('objects', 'Karambit_Knife.obj')
        self.earth = objLoader.load_obj_file('objects', 'Earth.obj')
        self.saturn = objLoader.load_obj_file('objects', 'saturn.obj')


    
    
    def init_lights(self):
        self.shader.set_global_light_direction(Vector(-0.2, -1.0, -0.3))
        self.shader.set_global_light_diffuse(Color(1, 1, 1))
        self.shader.set_global_light_direction2(Vector(0.2, -1.0, 0.3))
        self.shader.set_global_light_diffuse2(Color(1, 1, 1))

        
    # Texture loader
    def loadTexture(self,path):
        texture = pygame.image.load(path)
        tex_string = pygame.image.tostring(texture, "RGBA",1)
        width = texture.get_width()
        height = texture.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,tex_id)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width,height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
        return tex_id

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        velocity = self.player.velocity
        ##########
        # PLAYER #
        ##########
        if self.w_key_down:
            self.moveVec = Vector(0,0,-velocity*delta_time)
            self.view_matrix.slide(0,0,-velocity * delta_time)

        if self.s_key_down:
            self.moveVec = Vector(0,0,velocity*delta_time)
            self.view_matrix.slide(0,0,velocity * delta_time)
            
        if self.a_key_down:
            self.moveVec = Vector(-velocity*delta_time,0,0)
            self.view_matrix.slide(-velocity*delta_time,0,0)
            
        if self.d_key_down:
            self.moveVec = Vector(velocity*delta_time,0,0)
            self.view_matrix.slide(velocity*delta_time,0,0)

        if self.space_key_down:
            if not self.jumping:
                self.jumping = True
    
        ##########
        # Camera #
        ##########
        self.xPos, self.yPos = pygame.mouse.get_pos()

        if pygame.mouse.get_focused() != 0:
            self.firstMouse = False
        else:
            self.firstMouse = True

        if self.firstMouse:
            self.lastX = self.xPos
            self.lastY = self.yPos
        
        xOffset = self.xPos - self.lastX
        yOffset = self.yPos - self.lastY
        
        self.lastX = self.xPos
        self.lastY = self.yPos

        self.view_matrix.processMouseMovement(xOffset,yOffset)
        self.moveVec = Vector(0,0,0)

        # Keep player grounded
        if not self.jumping and not self.falling:
            self.view_matrix.eye.y = 0.2

        #update player pos
        self.player.update(Point(self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z))

        for shot in self.shotlist:
            shot.position += Vector(-shot.vector.x,0,-shot.vector.z)
            shot.update(shot.position)
            if shot.position.x < -10 or shot.position.x > 10:
                self.shotlist.remove(shot)
                continue
            if shot.position.z < -20 or shot.position.z > 10:
                self.shotlist.remove(shot)
            


        ###############
        #  Collision  #
        ###############
            for wall in self.wallList:
                if shot.checkIntersection(wall):
                    self.shotlist.remove(shot)
                    self.wallList.remove(wall)
            if self.enemyM != None:
                if shot.checkIntersection(self.enemyM):
                    self.shotlist.remove(shot)
                    self.enemyM = None
            
        for wall in self.wallList:
            if self.knifing:
                if self.player.checkIntersection(wall):
                    self.wallList.remove(wall)

            if self.player.checkIntersection(wall):
                self.player.doCollision(wall)

            
    

                

      

            
        ###############
        #   Jumping   #
        ###############

        if self.jumping:
            if self.player.position.y < 0.5:
                self.player.position.y += 0.5 * delta_time
            else:
                self.player.position.y = 0.5
                self.falling = True
                self.jumping = False

        if self.falling:
            if self.player.position.y >= 0.2:
                self.player.position.y -= 0.5 * delta_time
            else:
                self.falling = False
                self.player.position.y = 0.2
            
        # Set camera pos to player pos
        self.view_matrix.eye = self.player.position
        
        




    def display(self):
        
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.width, self.height)

        self.projection_matrix.set_perspective(self.fov, self.width/self.height, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.shader.set_eye_position(self.view_matrix.eye)


        self.shader.set_material_specular(Color(0.5, 0.5, 0.5))
        self.shader.set_material_shininess(10)
        self.model_matrix.load_identity()
        
        #BASE BEGIN
        ##FLOOR
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.wallTextureID)
        self.shader.set_diffuse_texture(0)
        self.shader.set_using_texture()
        #self.shader.set_material_diffuse(Color(1.0,1.0,1.0))
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,-0.45,-8.5)
        self.model_matrix.add_scale(10,0.1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,1)
        self.model_matrix.add_scale(10,1,1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-5,0,-7.5)
        self.model_matrix.add_scale(0.1,1,17)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        for wall in self.wallList:
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(wall.position.x,wall.position.y,wall.position.z)
            self.model_matrix.add_scale(wall.scale.x,wall.scale.y,wall.scale.z)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()

        

        pos = self.model_matrix.yaw(cos(radians(self.view_matrix.jaw)),sin(radians(self.view_matrix.jaw)),Point(self.player.position.x - 1, 0.1, self.player.position.z - 0.5),self.view_matrix.eye)

        
        
        if self.active_slot == 1:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D,self.rifleTextureID)
            self.shader.set_diffuse_texture(0)
            self.shader.set_using_texture()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(pos.x, self.player.position.y - 0.1,pos.z)
            self.model_matrix.add_scale(0.03,0.03,0.03)
            self.model_matrix.add_rotate_y(4.5)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw/60)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.rifle.draw(self.shader, True)
            self.model_matrix.pop_matrix()
        if self.active_slot == 2:
            self.shader.set_not_using_texture()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(pos.x, self.player.position.y - 0.1,pos.z)
            self.model_matrix.add_scale(0.04,0.04,0.04)
            self.model_matrix.add_rotate_x(1.5)
            self.model_matrix.add_rotate_z(3.5)
            self.model_matrix.add_rotate_z(self.view_matrix.jaw/60)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.pistol.draw(self.shader)
            self.model_matrix.pop_matrix()

        if self.active_slot == 3:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D,self.karambitTextureID)
            self.shader.set_diffuse_texture(0)
            self.shader.set_using_texture()

            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(pos.x, self.player.position.y - 0.2,pos.z)
            self.model_matrix.add_scale(0.1,0.1,0.1)
            self.model_matrix.add_rotate_z(90)
            self.model_matrix.add_rotate_x(5)
            self.model_matrix.add_rotate_y(-0.5)
            self.model_matrix.add_rotate_z(self.view_matrix.jaw/50)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.karambit.draw(self.shader, True)
            self.model_matrix.pop_matrix()

        for shot in self.shotlist:
            self.shader.set_material_diffuse(Color(1,0.5,0))
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(shot.position.x,shot.position.y,shot.position.z)
            self.model_matrix.add_scale(shot.scale.x,shot.scale.y,shot.scale.z)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()

        if self.enemyM != None:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D,self.playerTextureID)
            self.shader.set_diffuse_texture(0)
            self.shader.set_using_texture()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.enemyM.position.x,-0.3,self.enemyM.position.z)
            self.model_matrix.add_scale(0.1,0.1,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.enemy.draw(self.shader, True)
            self.model_matrix.pop_matrix()
            self.shader.set_not_using_texture()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.saturnTextureID)
        self.shader.set_diffuse_texture(0)
        self.shader.set_using_texture()
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0, 0.1, -3)
        self.model_matrix.add_scale(1,1,1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.saturn.draw(self.shader, True)
        self.model_matrix.pop_matrix()

        

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(3,-0.3,-5)
        # self.model_matrix.add_scale(0.005,0.005,0.005)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.sus.draw(self.shader, True)
        # self.model_matrix.pop_matrix()
        
        pygame.display.flip()


    def generateShot(self):
        shotpos = self.model_matrix.yaw(cos(radians(self.view_matrix.jaw)),sin(radians(self.view_matrix.jaw)),Point(self.player.position.x - 1.5, self.player.position.y, self.player.position.z - 0.5),self.view_matrix.eye)
        self.shotlist.append(GameObject(shotpos,Point(0.2,0.05,0.05),self.view_matrix.n))

    def animateKnife(self,x,y,z):
        self.model_matrix.add_rotate_z(z)
        self.model_matrix.add_rotate_x(x)
        self.model_matrix.add_rotate_y(y)
        self.model_matrix.add_rotate_z(self.view_matrix.jaw/50)
      
    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    print(event.type)
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                        
                    if event.key == K_UP:
                        self.UP_key_down = True

                    if event.key == K_w:
                        self.w_key_down = True

                    if event.key == K_s:
                        self.s_key_down = True

                    if event.key == K_a:
                        self.a_key_down = True

                    if event.key == K_d:
                        self.d_key_down = True

                    if event.key == K_SPACE:
                        self.space_key_down = True

                    if event.key == K_1:
                        self.active_slot = 1
                        self.player.velocity = 2

                    if event.key == K_2:
                        self.active_slot = 2
                        self.player.velocity = 2.2

                    if event.key == K_3:
                        self.active_slot = 3
                        self.player.velocity = 2.5

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if len(self.shotlist) < 26 and not self.active_slot == 3:
                        self.generateShot()
                    if self.active_slot == 3:
                        self.knifing = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.knifing = False

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False

                    if event.key == K_w:
                        self.w_key_down = False

                    if event.key == K_s:
                        self.s_key_down = False

                    if event.key == K_a:
                        self.a_key_down = False

                    if event.key == K_d:
                        self.d_key_down = False

                    
                    if event.key == K_SPACE:
                        self.space_key_down = False

            
            self.update()
            self.display()
            

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()