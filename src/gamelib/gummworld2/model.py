#!/usr/bin/env python

# This file is part of Gummworld2.
#
# Gummworld2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gummworld2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Gummworld2.  If not, see <http://www.gnu.org/licenses/>.

# Compatible: Python 2.7, Python 3.2

"""model.py - Physics model for Gummworld2."""

import pygame

from gummworld2 import Vec2d


__version__ = '$Id: model.py 407 2013-08-12 15:11:30Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'

__all__ = ['NoWorld', 'Object', 'World']


class NoWorld(object):
    
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
    
    def add(self, *args):
        pass
    
    def step(self, dt):
        pass


class Object(object):
    """An object model suitable for use as a Camera target or an autonomous
    object in World.
    
    Similar to pygame.sprite.Sprite, without the graphics and rect. Subclass
    this and extend.
    """
    
    def __init__(self, position=(0, 0)):
        self._position = Vec2d(position)
        self._worlds = {}
    
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        p = self._position
        p.x, p.y = val
    
    def update(self, *args):
        pass
    
    def worlds(self):
        return self._worlds.keys()
    
    def kill(self):
        for w in self._worlds:
            w.remove(self)
        self._worlds.clear()


class World(object):
    """A container for model.Objects.
    
    Similar to pygame.sprite.AbstractGroup. Not compatible with
    pygame.sprite.Sprite.
    
    If you want the world to store pygame sprites, substitute a group and that
    has a rect attribute and step() method.
    """
    
    def __init__(self, rect):
        """rect is bounding box edges in pygame space"""
        self.rect = pygame.Rect(rect)
        self._object_dict = {}
    
    def add(self, *objs):
        """Add objects to the world."""
        for o in objs:
            self._object_dict[o] = 1
            if not hasattr(o, '_worlds'):
                o._worlds = {}
            o._worlds[self] = 1
    
    def remove(self, *objs):
        for o in objs:
            if o in self._object_dict:
                del self._object_dict[o]
            if hasattr(o, '_worlds') and self in o._worlds:
                del o._worlds[self]
    
    def objects(self):
        return self._object_dict.keys()
    
    def step(self, dt):
        for o in self.objects():
            o.update()
    
    def __iter__(self):
        return iter(self.objects())
    
    def __contains__(self, obj):
        return obj in self._object_dict
    
    def __nonzero__(self):
        return len(self._object_dict) != 0
    
    def __len__(self):
        """len(group)
           number of sprites in group
    
           Returns the number of sprites contained in the group."""
        return len(self._object_dict)
    
    def __repr__(self):
        return "<%s(%d objects)>" % (self.__class__.__name__, len(self))
