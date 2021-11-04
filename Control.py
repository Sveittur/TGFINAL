
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

from OpenGL.GL.images import PIXEL_NAMES
from OpenGL.GLU import *
from math import *
import random
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
from soundBoard import * 
from challenges import *


import objLoader

import requests



class GraphicsProgram3D:
    def __init__(self):

        pygame.init()
        self.width = 1280
        self.height = 600
        self.gameDisplay = pygame.display.set_mode((self.width,self.height), pygame.OPENGL|pygame.DOUBLEBUF)


        self.sprite_shader = SpriteShader()
        self.sprite_shader.use()
        self.shader = Shader3D()
        self.shader.use()
        
        

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(5,0.2,0), Point(0,0.2,0),Vector(0,1,0))
        self.view_matrix.eye = Point(0,0.2,-9)

        self.projection_matrix = ProjectionMatrix()
        self.fov = 60*pi/180 # 80 deg
        self.projection_matrix.set_perspective(pi/2, self.width/self.height, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.init_lights()
        self.player = player(Point(0,0.2,0))
        self.sprite = Sprite()
        self.sky_sphere = SkySphere(128,256)

        self.challengeBox = GameObject(Point(0,0,-11),Point(0.5,0.5,0.5))
        self.winning = False
        self.losing = False
        self.begin = False

        self.enemyList = [#up
                          GameObject(Point(6,-0.3,0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(9,-0.3,0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(3,-0.3,-1),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-4,-0.3,-1),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-7,-0.3,0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-8,-0.3,0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-9,-0.3,0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-6,-0.3,-0.5),Point(0.5,1,0.5),None,pi),
                          GameObject(Point(-5,-0.3,0),Point(0.5,1,0.5),None,pi),
                          #down
                          GameObject(Point(6,-0.3,-12),Point(0.5,1,0.5)),
                          GameObject(Point(9,-0.3,-13),Point(0.5,1,0.5)),
                          GameObject(Point(3,-0.3,-16),Point(0.5,1,0.5)),
                          GameObject(Point(-4,-0.3,-15),Point(0.5,1,0.5)),
                          GameObject(Point(-7,-0.3,-12),Point(0.5,1,0.5)),
                          GameObject(Point(-8,-0.3,-11),Point(0.5,1,0.5)),
                          GameObject(Point(-9,-0.3,-15),Point(0.5,1,0.5)),
                          GameObject(Point(-6,-0.3,-16),Point(0.5,1,0.5)),
                          GameObject(Point(-5,-0.3,-13),Point(0.5,1,0.5)),
                          #left
                          GameObject(Point(9,-0.3,-1),Point(0.5,0.5,0.5),None,-pi/2),
                          GameObject(Point(8.5,-0.3,-2),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(9,-0.3,-3),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(8.5,-0.3,-4),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(9,-0.3,-5),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(8,-0.3,-6),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(9,-0.3,-7),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(9,-0.3,-8),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(8.5,-0.3,-9),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(8,-0.3,-10),Point(0.5,1,0.5),None,-pi/2),
                          GameObject(Point(8.5,-0.3,-11),Point(0.5,1,0.5),None,-pi/2),
                          #right
                          GameObject(Point(-7,-0.3,-1),Point(0.5,0.5,0.5),None,pi/2),
                          GameObject(Point(-6.5,-0.3,-2),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-7,-0.3,-3),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-6.5,-0.3,-4),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-7,-0.3,-5),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-6,-0.3,-6),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-7,-0.3,-7),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-7,-0.3,-8),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-6.5,-0.3,-9),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-6,-0.3,-10),Point(0.5,1,0.5),None,pi/2),
                          GameObject(Point(-6.5,-0.3,-11),Point(0.5,1,0.5),None,pi/2),
                        ]
        self.activeEnemyList = []
        self.enemyList = list(set(self.enemyList))
        for i in range(0, int((len(self.enemyList)-1)/2)):
            newEnemy = self.spawnEnemy()
            self.activeEnemyList.append(newEnemy)
        self.activeEnemyList = list(set(self.activeEnemyList))
        
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
        self.stage = 2


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
        self.skyTextureID = self.loadTexture('texture/sky.jpeg')
        self.hitmarkerColorTextureID  = self.loadTexture('texture/hitmarker.png')
        self.hitmarkerAlphaTextureID  = self.loadTexture('texture/hitmarkerAlpha.png')
        self.crosshairTextureID = self.loadTexture('texture/crosshair.png')
        self.crosshairAlphaTextureID = self.loadTexture('texture/crosshairAlpha.png')
        self.youWinTextureID = self.loadTexture('texture/YOUWIN.png')
        self.youWinAlphaTextureID = self.loadTexture('texture/YOUWINALPHA.png')
        self.youLoseTextureID = self.loadTexture('texture/YOULOSE.png')
        self.youLoseAlphaTextureID = self.loadTexture('texture/YOULOSEALPHA.png')
        self.startTextureID = self.loadTexture('texture/START.png')
        self.startAlphaTextureID = self.loadTexture('texture/STARTALPHA.png')
        self.circleColorTextureID = self.loadTexture('texture/CIRCLECOLOR.png')
        self.circleColorAlphaTextureID = self.loadTexture('texture/CIRCLECOLORALPHA.png')
        self.gameWonTextureID = self.loadTexture('texture/GAMEWON.png')
        self.gameWonAlphaTextureID = self.loadTexture('texture/GAMEWONALPHA.png')
        self.stage1TextureID = self.loadTexture('texture/STAGE1.png')
        self.stage1AlphaTextureID = self.loadTexture('texture/STAGE1ALPHA.png')
        self.stage2TextureID = self.loadTexture('texture/STAGE2.png')
        self.stage2AlphaTextureID = self.loadTexture('texture/STAGE2ALPHA.png')
        self.targetTextureID = self.loadTexture('texture/TARGET.png')
        self.targetAlphaTextureID = self.loadTexture('texture/TARGETALPHA.png')



        # OBJECTS
        self.pistol = objLoader.load_obj_file('objects','M9.obj')
        self.rifle = objLoader.load_obj_file('objects','ak.obj')
        self.enemy = objLoader.load_obj_file('objects','human.obj')
        self.karambit = objLoader.load_obj_file('objects', 'Karambit_Knife.obj')
        self.saturn = objLoader.load_obj_file('objects', 'saturn.obj')
        self.crosshair = objLoader.load_obj_file('objects','sphere.obj')

        # SHOUNDS
        self.soundboard = soundBoard()

        # CHALLENGES
        self.aimbots = aimbots()
        self.flick = flickGame()


        




    
    
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
        self.activeEnemyList = list(set(self.activeEnemyList))
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
            shot.position += Vector(-shot.vector.x/2,-shot.vector.y/2,-shot.vector.z/2)
            shot.update(shot.position)
            if shot.position.x < -20 or shot.position.x > 20:
                self.shotlist.remove(shot)
                continue
            if shot.position.z < -20 or shot.position.z > 20:
                self.shotlist.remove(shot)
                continue

            
        

        ###############
        #  Collision  #
        ###############

            #aimbots Box
            if shot.checkIntersection(self.challengeBox) and self.aimbots.active == False and self.flick.active == False:
                if self.stage == 1:
                    self.aimbots.startChallenge()
                if self.stage == 2:
                    self.flick.startChallenge()
                self.begin = True
                self.stopwatch = stopwatch()

            ###########
            # STAGE 2 #
            ###########
            if self.stage == 2:
                if self.flick.circle.checkIntersection(shot):
                    if self.flick.active:
                        self.flick.killCount += 1
                        self.flick.updateCircle()
                        self.shotlist.remove(shot)
                        continue

            ###########
            # STAGE 1 #
            ###########

            if self.stage == 1:
                for enemy in self.activeEnemyList:
                    if shot.checkIntersection(enemy):
                        if self.shotlist == []:
                            continue
                        if self.active_slot == 3:
                            enemy.health -= 100
                            
                        if self.active_slot == 2:
                            enemy.health -= 14
                        if self.active_slot == 1:
                            enemy.health -= 34
                            if enemy.maxY - shot.position.y <= 0.08:
                                enemy.health -= 76
                                self.soundboard.playHeadshot()

                        if enemy.health <= 0:
                            enemy.health = 100
                            self.activeEnemyList.remove(enemy)
                            newEnemy = self.spawnEnemy(enemy)
                            self.activeEnemyList.append(newEnemy)
                            self.activeEnemyList = list(set(self.activeEnemyList))
                            if self.aimbots.active:
                                self.aimbots.killCount += 1
                
                        if shot in self.shotlist:
                            self.shotlist.remove(shot)

            
        if self.stage == 1:
            for enemy in self.activeEnemyList:
                if self.player.checkIntersection(enemy):
                    if self.knifing:
                        self.soundboard.stopKnifeWiff()
                        self.soundboard.playKnifeKill()
                        self.activeEnemyList.remove(enemy)
                        newEnemy = self.spawnEnemy()
                        self.activeEnemyList.append(newEnemy)
                    self.player.doCollision(enemy)


       
        

            
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
        if self.aimbots.active:
            for enemy in self.activeEnemyList:
                if self.aimbots.dir == "right":
                    if enemy.yRotation == None:
                        enemy.position.x -= 0.5 * delta_time

                    if enemy.yRotation == pi:
                        enemy.position.x += 0.5 * delta_time

                    if enemy.yRotation == pi/2:
                        enemy.position.z += 0.5 * delta_time

                    if enemy.yRotation == -pi/2:
                        enemy.position.z -= 0.5 * delta_time

                elif self.aimbots.dir == "left":
                    if enemy.yRotation == None:
                        enemy.position.x += 0.5 * delta_time

                    if enemy.yRotation == pi:
                        enemy.position.x -= 0.5 * delta_time

                    if enemy.yRotation == pi/2:
                        enemy.position.z -= 0.5 * delta_time
                        
                    if enemy.yRotation == -pi/2:
                        enemy.position.z += 0.5 * delta_time
                enemy.update()

            if int (self.aimbots.stopwatch.elapsedTime()) % 2 == 0:
                if self.aimbots.dir == "right":
                    self.aimbots.dir = "left"
                else:
                    self.aimbots.dir = "right"

            if self.aimbots.killCount == 10:
                self.aimbots.stopChallenge()
                if self.aimbots.checkWin():
                    self.winning = True
                    self.stopwatch = stopwatch()
                else:
                    self.losing = True
                    self.stopwatch = stopwatch()
                    
        if self.flick.active:
            if self.flick.killCount == 30:
                self.flick.stopChallenge()
                if self.flick.checkWin():
                    self.winning = True
                    self.stopwatch = stopwatch()
                else:
                    self.losing = True
                    self.stopwatch = stopwatch()

        if self.winning:
            print(self.stopwatch.elapsedTime())
            if self.stopwatch.elapsedTime() > 4:
                self.winning = False
                self.stage += 1
        if self.losing:
            if self.stopwatch.elapsedTime() > 4:
                self.losing = False

        if self.begin:
            if self.stopwatch.elapsedTime() > 1:
                self.begin = False
                    
                       
        




    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###
        glEnable(GL_FRAMEBUFFER_SRGB)
        glShadeModel(GL_SMOOTH)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.width, self.height)

        self.model_matrix.load_identity()
        self.sprite_shader.use()
        self.sprite_shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.sprite_shader.set_view_matrix(self.view_matrix.get_matrix())
        
        glDisable(GL_DEPTH_TEST)
        if self.stage == 1:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.skyTextureID)
            self.sprite_shader.set_diffuse_texture(0)
            self.sprite_shader.set_alpha_texture(None)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z - 0.08)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sky_sphere.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()
            glEnable(GL_DEPTH_TEST)
            glClear(GL_DEPTH_BUFFER_BIT)
        if self.stage == 2:
            # glActiveTexture(GL_TEXTURE0)
            # glBindTexture(GL_TEXTURE_2D, self.skyTextureID)
            # self.sprite_shader.set_diffuse_texture(0)
            # self.sprite_shader.set_alpha_texture(None)
            # self.sprite_shader.set_opacity(1.0)
            # self.model_matrix.push_matrix()
            # self.model_matrix.add_translation(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z - 0.08)
            # self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            # self.sky_sphere.draw(self.sprite_shader)
            # self.model_matrix.pop_matrix()
            # glEnable(GL_DEPTH_TEST)
            # glClear(GL_DEPTH_BUFFER_BIT)


        self.shader.use()
        self.projection_matrix.set_perspective(self.fov , self.width/self.height, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.shader.set_eye_position(self.view_matrix.eye)


        self.shader.set_material_specular(Color(0.5, 0.5, 0.5))
        self.shader.set_material_shininess(10)
        self.model_matrix.load_identity()
        
        if self.stage == 1:
            self.displayChallenge1()
        if self.stage == 2:
            self.displayChallenge2()

        

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

        glDisable(GL_DEPTH_TEST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.sprite_shader.use()
        self.sprite_shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.sprite_shader.set_view_matrix(self.view_matrix.get_matrix())
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.crosshairTextureID)
        self.sprite_shader.set_diffuse_texture(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.crosshairAlphaTextureID)
        self.sprite_shader.set_alpha_texture(1)
        self.sprite_shader.set_opacity(1.0)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
        self.model_matrix.add_rotate_y(pi/2)
        self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
        self.model_matrix.add_scale(0.1, 0.1, 0.1)
        self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
        self.sprite.draw(self.sprite_shader)
        self.model_matrix.pop_matrix()

        # You win screen
        if self.winning:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.youWinTextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.youWinAlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
            self.model_matrix.add_rotate_y(pi/2)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
            self.model_matrix.add_scale(1, 1, 1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        if self.losing:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.youLoseTextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.youLoseAlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
            self.model_matrix.add_rotate_y(pi/2)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
            self.model_matrix.add_scale(1, 1, 1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        if self.begin:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.startTextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.startAlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
            self.model_matrix.add_rotate_y(pi/2)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
            self.model_matrix.add_scale(1, 1, 1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        if self.stage == 1 and self.begin == False and self.aimbots.active == False and self.aimbots.killCount == None:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.stage1TextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.stage1AlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
            self.model_matrix.add_rotate_y(pi/2)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
            self.model_matrix.add_scale(1, 1, 1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        if self.stage == 2 and self.begin == False and self.flick.active == False and self.flick.killCount == None:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.stage2TextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.stage2AlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.view_matrix.eye.x-self.view_matrix.n.x, self.view_matrix.eye.y - self.view_matrix.n.y, self.view_matrix.eye.z-self.view_matrix.n.z)
            self.model_matrix.add_rotate_y(pi/2)
            self.model_matrix.add_rotate_y(-self.view_matrix.jaw*pi/180)
            self.model_matrix.add_scale(1, 1, 1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        if self.stage == 2:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.targetTextureID)
            self.sprite_shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.targetAlphaTextureID)
            self.sprite_shader.set_alpha_texture(1)
            self.sprite_shader.set_opacity(1.0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.flick.circle.position.x, self.flick.circle.position.y, self.flick.circle.position.z)
            self.model_matrix.add_scale(2,1,1)
            self.sprite_shader.set_model_matrix(self.model_matrix.matrix)
            self.sprite.draw(self.sprite_shader)
            self.model_matrix.pop_matrix()

        
        glDisable(GL_BLEND)


        
        pygame.display.flip()


    def generateShot(self):
        shotpos = self.model_matrix.yaw(cos(radians(self.view_matrix.jaw)),sin(radians(self.view_matrix.jaw)),Point(self.player.position.x - 1.5, self.player.position.y, self.player.position.z - 0.5),self.view_matrix.eye)
        self.shotlist.append(GameObject(self.player.position,Point(0.2,0.05,0.05),self.view_matrix.n))

    def animateKnife(self,x,y,z):
        self.model_matrix.add_rotate_z(z)
        self.model_matrix.add_rotate_x(x)
        self.model_matrix.add_rotate_y(y)
        self.model_matrix.add_rotate_z(self.view_matrix.jaw/50)

    def spawnEnemy(self, lastEnemy = None):
        newEnemy = self.enemyList[randint(0,len(self.enemyList)-1)]
        while newEnemy in self.activeEnemyList or lastEnemy == newEnemy:
            newEnemy = self.enemyList[randint(0,len(self.enemyList)-1)]
        return newEnemy

    def displayChallenge1(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.wallTextureID)
        self.shader.set_diffuse_texture(0)
        self.shader.set_using_texture()

        #CHALLANGE BOX
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.challengeBox.position.x,self.challengeBox.position.y,self.challengeBox.position.z )
        self.model_matrix.add_scale(self.challengeBox.scale.x,self.challengeBox.scale.y,self.challengeBox.scale.z)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        #floor
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,-0.45,-8.5)
        self.model_matrix.add_scale(19,0.1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
        
        
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-9.5,0,-8.5)
        self.model_matrix.add_scale(0.1,1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,-18)
        self.model_matrix.add_scale(19,1,0.1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
        #LEFT
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,1)
        self.model_matrix.add_scale(19,1,0.1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
        #BOTTOM
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(9.5,0,-8.5)
        self.model_matrix.add_scale(0.1,1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()


        ###################
        # Drawing Enemies #
        ###################
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.playerTextureID)
        self.shader.set_diffuse_texture(0)
        self.shader.set_using_texture()
        for enemy in self.activeEnemyList:
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(enemy.position.x,-0.4,enemy.position.z)
            if enemy.yRotation != None:
                self.model_matrix.add_rotate_y(enemy.yRotation)
            self.model_matrix.add_scale(0.1,0.1,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.enemy.draw(self.shader, True)
            self.model_matrix.pop_matrix()
        self.shader.set_not_using_texture()


    def displayChallenge2(self):

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.wallTextureID)
        self.shader.set_diffuse_texture(0)
        self.shader.set_using_texture()

        #CHALLANGE BOX
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.challengeBox.position.x,self.challengeBox.position.y,self.challengeBox.position.z )
        self.model_matrix.add_scale(self.challengeBox.scale.x,self.challengeBox.scale.y,self.challengeBox.scale.z)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
        
        #floor
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,-0.45,-8.5)
        self.model_matrix.add_scale(19,0.1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

       
        #wall
        self.shader.set_material_diffuse(Color(100,100,100))
        self.shader.set_not_using_texture()
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,0)
        self.model_matrix.add_scale(19,10,1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                        
                    if event.key == K_UP:
                        self.UP_key_down = True
                        self.aimbots.startChallenge()

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
                        if self.active_slot != 1:
                            self.active_slot = 1
                            self.player.velocity = 2
                            self.soundboard.stopPistolDeploy()
                            self.soundboard.stopKnifeDeploy()
                            self.soundboard.playAkDeploy()

                    if event.key == K_2:
                        if self.active_slot != 2:
                            self.active_slot = 2
                            self.player.velocity = 2.2
                            self.soundboard.stopAkDeploy()
                            self.soundboard.stopKnifeDeploy()
                            self.soundboard.playPistolDeploy()

                    if event.key == K_3:
                        if self.active_slot != 3:
                            self.active_slot = 3
                            self.player.velocity = 2.5
                            self.soundboard.stopPistolDeploy()
                            self.soundboard.stopAkDeploy()
                            self.soundboard.playKnifeDeploy()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if len(self.shotlist) < 26 and not self.active_slot == 3:
                        self.generateShot()
                        if self.active_slot == 1:
                            self.soundboard.playAkShoot()
                        elif self.active_slot == 2:
                            self.soundboard.playPistolShoot()
                    if self.active_slot == 3:
                        self.soundboard.playKnifeWiff()
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