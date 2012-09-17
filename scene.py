
import sys
import time

import numpy as np
import numpy.linalg as la
import transformations as tr

import random as rnd

from OpenGL.GL import *
from OpenGL.GLU import *

import math as m

if sys.platform.startswith('win'):
    timer = time.clock
else:
    timer = time.time

VERTS_NUM = 1000
SPACE_MAX = 20
SPACE_WIDE = 10
C = 1.5

PATH_NUM = 2048
DT = .1

class Scene :
	def __init__( self , fovy , ratio , near , far ) :
		self.fovy = fovy
		self.near = near 
		self.far = far
		self.ratio = ratio

		self._init_scene()

		self.x = 0.0

		self.last_time = timer()

		self.plane_alpha = 65.0 / 180.0 * m.pi

		self.lpos = [ 1 ,-1 , 0 ]

	def gfx_init( self ) :
		self._update_proj()

	def draw( self ) :
		self._update_proj()

		self.time = timer()

		dt = self.time - self.last_time

		self._step( dt )

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		glPointSize(2)

		self._draw_scene()

		self.x+=dt*.3

		self.last_time = self.time

	def _init_scene( self ) :
		self.verts = []
		for i in range(0,VERTS_NUM) :
			self.verts.append( rnd.uniform(-SPACE_MAX*SPACE_WIDE,SPACE_MAX*SPACE_WIDE) )
			self.verts.append( rnd.uniform(-SPACE_MAX   ,SPACE_MAX   ) )
		self.verts = np.array(self.verts , np.float32 )
		self.lorentz = np.zeros(len(self.verts) , np.float32 )
		self.v = 0
		self.t = 0

		self.path = np.zeros(PATH_NUM*2)
		t = DT
		for i in range(1,PATH_NUM) :
#        for i in range(PATH_NUM/2,PATH_NUM) :
			t += DT
			self.path[i*2  ] = self.path[i*2-2] + m.sin( t * .08 ) * C * .5 * DT
			self.path[i*2+1] = t
		self.lpath = np.zeros(len(self.path))

	def _step( self , dt ) :
		self.t+= dt
		self.v = m.sin(self.t*.08) * C * .5

		roll = False

		for i in range(PATH_NUM) :
			self.path[i*2  ] -= self.v*dt
			self.path[i*2+1] -= dt

#            if self.path[i*2+1] > 0 and self.path[i*2+1] - dt < 0 :
#                roll = True

#        if roll :
#            np.roll(self.path,2)
#            t = self.path[PATH_NUM-3] + DT
#            self.path[PATH_NUM-2] = self.path[PATH_NUM-4] + m.sin(t*.08)*C*.5*DT
#            self.path[PATH_NUM-1] = t


		for i in range(VERTS_NUM) :
			self.verts[i*2  ] += self.v*dt
			self.verts[i*2+1] += dt
			if self.verts[i*2+1] >= SPACE_MAX :
				self.verts[i*2+1] -= SPACE_MAX*2

		B = self.v / C 
		G = 1.0 / m.sqrt( 1 - B**2 )
		v = self.v

		for i in range(VERTS_NUM) :
			x = self.verts[i*2  ]
			t = self.verts[i*2+1]
			self.lorentz[i*2  ] = G*( x - v*t       )
			self.lorentz[i*2+1] = G*( t -(v*x)/C**2 )

		for i in range(PATH_NUM) :
			x = self.path[i*2  ]
			t = self.path[i*2+1]
			self.lpath[i*2  ] = G*( x - v*t       )
			self.lpath[i*2+1] = G*( t -(v*x)/C**2 )

	def _draw_scene( self ) :
		glColor3f(.1,.1,.1)
		glBegin(GL_LINES)
		glVertex2f( SPACE_MAX, SPACE_MAX)
		glVertex2f(-SPACE_MAX,-SPACE_MAX)
		glVertex2f(-SPACE_MAX, SPACE_MAX)
		glVertex2f( SPACE_MAX,-SPACE_MAX)
		glEnd()

		glEnableClientState(GL_VERTEX_ARRAY)

		glColor3f(1,1,1)
		glVertexPointer( 2 , GL_FLOAT , 0 , self.lorentz )
		glDrawArrays( GL_POINTS , 0 , len(self.lorentz)/2 )

		glColor3f(1,.5,0)
		glVertexPointer( 2 , GL_FLOAT , 0 , self.lpath )
		glDrawArrays( GL_LINE_STRIP , 0 , len(self.lpath)/2 )

		glDisableClientState(GL_VERTEX_ARRAY)

	def _update_proj( self ) :
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-SPACE_MAX,SPACE_MAX,-SPACE_MAX,SPACE_MAX)
		glMatrixMode(GL_MODELVIEW)

	def set_fov( self , fov ) :
		self.fov = fov
		self._update_proj()

	def set_near( self , near ) :
		self.near = near
		self._update_proj()

	def set_ratio( self , ratio ) :
		self.ratio = ratio
		self._update_proj()

	def set_screen_size( self , w , h ) :
		self.width  = w 
		self.height = h
		self.set_ratio( float(w)/float(h) )

	def mouse_move( self , df , buts ) :
		pass

	def key_pressed( self , mv ) :
		pass

