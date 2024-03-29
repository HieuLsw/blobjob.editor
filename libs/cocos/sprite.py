# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''Sprite

Animating a sprite
==================

To execute any action you need to create an action::

    move = MoveBy( (50,0), 5 )

In this case, ``move`` is an action that will move the sprite
50 pixels to the right (``x`` coordinate) and  0 pixel in the ``y`` coordinate
in 5 seconds.

And now tell the sprite to execute it::

    sprite.do( move )
'''

__docformat__ = 'restructuredtext'
import math

import pyglet
from pyglet import image
from pyglet.gl import *

import cocosnode
from batch import *
import rect

import euclid
import math

__all__ = [ 'Sprite',                     # Sprite class
            ]



class Sprite( BatchableNode, pyglet.sprite.Sprite):
    '''Sprites are sprites that can execute actions.

    Example::

        sprite = Sprite('grossini.png')
    '''

    def __init__( self, image, position=(0,0), rotation=0, scale=1, opacity = 255, color=(255,255,255), anchor = None ):
        '''Initialize the sprite

        :Parameters:
                `image` : string or image
                    name of the image resource or a pyglet image.
                `position` : tuple
                    position of the anchor. Defaults to (0,0)
                `rotation` : float
                    the rotation (degrees). Defaults to 0.
                `scale` : float
                    the zoom factor. Defaults to 1.
                `opacity` : int
                    the opacity (0=transparent, 255=opaque). Defaults to 255.
                `color` : tuple
                    the color to colorize the child (RGB 3-tuple). Defaults to (255,255,255).
                `anchor` : (float, float)
                    (x,y)-point from where the image will be positions, rotated and scaled in pixels. For example (image.width/2, image.height/2) is the center (default).
        '''

        if isinstance(image, str):
            image = pyglet.resource.image(image)

        self.transform_anchor_x = 0
        self.transform_anchor_y = 0
        self._image_anchor_x = 0
        self._image_anchor_y = 0

        pyglet.sprite.Sprite.__init__(self, image)
        BatchableNode.__init__(self)



        if anchor is None:
            if isinstance(self.image, pyglet.image.Animation):
                anchor = (image.frames[0].image.width / 2,
                    image.frames[0].image.height / 2)
            else:
                anchor = image.width / 2, image.height / 2


        self.image_anchor = anchor

        # group.
        # This is for batching
        self.group = None

        # children group.
        # This is for batching
        self.children_group = None

        #: position of the sprite in (x,y) coordinates
        self.position = position

        #: rotation degrees of the sprite. Default: 0 degrees
        self.rotation = rotation

        #: scale of the sprite where 1.0 the default value
        self.scale = scale

        #: opacity of the sprite where 0 is transparent and 255 is solid
        self.opacity = opacity

        #: color of the sprite in R,G,B format where 0,0,0 is black and 255,255,255 is white
        self.color = color


    def get_rect(self):
        '''Get a cocos.rect.Rect for this sprite.'''
        x = -self.image_anchor_x
        y = -self.image_anchor_y
        return rect.Rect(x,y,self.width, self.height)

    def get_AABB(self):
        '''Returns a local-coordinates Axis aligned Bounding Box'''

        v = self._vertex_list.vertices
        x = v[0], v[2], v[4], v[6]
        y = v[1], v[3], v[5], v[7]
        return rect.Rect(min(x),min(y),max(x)-min(x),max(y)-min(y))

    def _set_rotation( self, a ):
        pyglet.sprite.Sprite._set_rotation(self, a)
        BatchableNode._set_rotation(self,a)

    def _set_scale( self, s ):
        pyglet.sprite.Sprite._set_scale(self,s)
        BatchableNode._set_scale(self,s)

    def _set_position( self, p ):
        pyglet.sprite.Sprite.position = p
        BatchableNode._set_position(self,p)

    def _set_x(self, x ):
        pyglet.sprite.Sprite._set_x( self, x )
        BatchableNode._set_x( self, x)

    def _set_y(self, y ):
        pyglet.sprite.Sprite._set_y( self, y )
        BatchableNode._set_y( self, y)

    def contains(self, x, y):
        '''Test whether this (untransformed) Sprite contains the pixel coordinates
        given.
        '''
        sx, sy = self.position
        ax, ay = self.image_anchor
        sx -= ax
        sy -= ay
        if x < sx or x > sx + self.width: return False
        if y < sy or y > sy + self.height: return False
        return True


    def _set_anchor_x(self, value):
        self._image_anchor_x = value
        self._update_position()

    def _get_anchor_x(self):
        return self._image_anchor_x
    image_anchor_x = property(_get_anchor_x, _set_anchor_x)

    def _set_anchor_y(self, value):
        self._image_anchor_y = value
        self._update_position()

    def _get_anchor_y(self):
        return self._image_anchor_y
    image_anchor_y = property(_get_anchor_y, _set_anchor_y)

    def _set_anchor(self, value):
        self._image_anchor_x = value[0]
        self._image_anchor_y = value[1]
        self._update_position()

    def _get_anchor(self):
        return (self._get_anchor_x(), self._get_anchor_y())

    image_anchor = property(_get_anchor, _set_anchor)

    def draw(self):
        self._group.set_state()
        if self._vertex_list is not None:
            self._vertex_list.draw(GL_QUADS)
        self._group.unset_state()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices[:] = [0, 0, 0, 0, 0, 0, 0, 0]
            return

        img = self._texture
        if self.transform_anchor_x == self.transform_anchor_y == 0:

            if self._rotation:
                x1 = -self._image_anchor_x * self._scale
                y1 = -self._image_anchor_y * self._scale
                x2 = x1 + img.width * self._scale
                y2 = y1 + img.height * self._scale
                x = self._x
                y = self._y

                r = -math.radians(self._rotation)
                cr = math.cos(r)
                sr = math.sin(r)
                ax = int(x1 * cr - y1 * sr + x)
                ay = int(x1 * sr + y1 * cr + y)
                bx = int(x2 * cr - y1 * sr + x)
                by = int(x2 * sr + y1 * cr + y)
                cx = int(x2 * cr - y2 * sr + x)
                cy = int(x2 * sr + y2 * cr + y)
                dx = int(x1 * cr - y2 * sr + x)
                dy = int(x1 * sr + y2 * cr + y)

                self._vertex_list.vertices[:] = [ax, ay, bx, by, cx, cy, dx, dy]
            elif self._scale != 1.0:
                x1 = int(self._x - self._image_anchor_x * self._scale)
                y1 = int(self._y - self._image_anchor_y * self._scale)
                x2 = int(x1 + img.width * self._scale)
                y2 = int(y1 + img.height * self._scale)
                self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
            else:
                x1 = int(self._x - self._image_anchor_x)
                y1 = int(self._y - self._image_anchor_y)
                x2 = x1 + img.width
                y2 = y1 + img.height
                self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
        else:
            x1 = int(- self._image_anchor_x)
            y1 = int(- self._image_anchor_y)
            x2 = x1 + img.width
            y2 = y1 + img.height
            m = self.get_local_transform()
            p1 = m * euclid.Point2(x1, y1)
            p2 = m * euclid.Point2(x2, y1)
            p3 = m * euclid.Point2(x2, y2)
            p4 = m * euclid.Point2(x1, y2)

            self._vertex_list.vertices[:] = [
                int(p1.x), int(p1.y), int(p2.x), int(p2.y),
                int(p3.x), int(p3.y), int(p4.x), int(p4.y)]

Sprite.supported_classes = Sprite
