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

"""spatialhash.py - High performance spatial hash for spatial
partitioning and fast collision detection.

Objects (other than geometry.LineGeometry) must have a pygame Rect attribute.
Optionally, objects may have a collided static method attribute for lower-level
collision detection (see the gummworld2.geometry module).

Objects that are outside the world bounding rect are ignored by add().

As of v0.5.0 SpatialHash will sort objects returned by most methods that return
a list of objects. See the methods' docstrings. In order to have the objects
sorted set the SpatialHash's sort_key method. This is the same key that is
passed to sort(key=func) and sorted(key=func), e.g.:
key=lambda obj: obj.rect.bottom.

This module is derived from the article and source code written by Conkerjo at
http://conkerjo.wordpress.com/2009/06/13/spatial-hashing-implementation-for-fast-2d-collisions/.
"""

__version__ = '$Id: spatialhash.py 429 2013-09-03 04:26:00Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'

__all__ = ['SpatialHash']


import time
from math import ceil
from weakref import WeakKeyDictionary

import pygame
from pygame.locals import Rect

if __name__ == '__main__':
    import paths

from gummworld2 import geometry


class SpatialHash(object):
    
    def __init__(self, world_rect, cell_size):
        ## Must inflate world rect by 1. This is because pygame rects consider
        ## the right and bottom borders to have zero units width. But the
        ## hashing calculates those as one unit width. Thus, taking pygame
        ## rect space at face value will attempt to access non-existant buckets
        ## at the corner cases.
        world_rect = world_rect.inflate(1, 1)
        
        self.rect = Rect(world_rect)
        self.bounds = (
            world_rect[0],
            world_rect[1],
            world_rect[0] + world_rect[2],
            world_rect[1] + world_rect[3],
        )
        self.cell_size = int(cell_size)
        
        self.rows = int(ceil(world_rect.h / float(cell_size))) + 1
        self.cols = int(ceil(world_rect.w / float(cell_size))) + 1
        self.buckets = [[] for i in range(self.rows * self.cols)]
        ## cell_ids = {obj1:[cells...], obj2:[cells...], ...}
        self.cell_ids = WeakKeyDictionary()
        
        self.num_buckets = len(self.buckets)
        
        self.coll_tests = 0
        self._temp_rect = pygame.Rect(0, 0, 0, 0)
        
        self.sort_key = None
        self.dirty = False
        self.sorted_objects = []
    
    @property
    def objects(self):
        """Return the entire list of objects.
        
        This method honors self.sort_key.
        """
        if self.sort_key:
            if self.dirty:
                self.sorted_objects[:] = sorted(
                    self.cell_ids, key=self.sort_key)
                self.dirty = False
            return self.sorted_objects[:]
        else:
            return self.cell_ids.keys()
    
    def add(self, obj):
        """Add or re-add obj. Return True if in bounds, else return False.
        
        If this method returns False then the object is completely out of
        bounds and cannot be stored in this space.
        
        Note that when obj changes its position, you must add it again so that
        its cell membership is updated. This method first removes the object if
        it is already in the spatial hash.
        """
        self.dirty = True
        try:
            cell_ids = self.intersect_indices(obj.rect)
        except AttributeError:
            rect = self._get_rect_for_line(obj)
            cell_ids = self.intersect_indices(rect)
        if obj in self.cell_ids and cell_ids == self.cell_ids[obj]:
            return cell_ids == True
        self.remove(obj)
        buckets = self.buckets
        for idx in cell_ids:
            buckets[idx].append(obj)
        self.cell_ids[obj] = cell_ids
        return cell_ids == True
    
    def addlist(self, objs):
        self.dirty = True
        all_good = True
        intersect_indices = self.intersect_indices
        _get_rect_for_line = self._get_rect_for_line
        self_cell_ids = self.cell_ids
        remove = self.remove
        buckets = self.buckets
        for obj in objs:
            try:
                cell_ids = intersect_indices(obj.rect)
            except AttributeError:
                rect = _get_rect_for_line(obj)
                cell_ids = intersect_indices(rect)
            if obj in self_cell_ids and cell_ids == self_cell_ids[obj]:
                # obj is still in same cell ids; save some CPU
                continue
            remove(obj)
            for idx in cell_ids:
                try:
                    buckets[idx].append(obj)
                except IndexError:
                    print('IndexError: buckets[{0}]'.format(idx))
                    print('len(buckets): {0}'.format(len(buckets)))
            self_cell_ids[obj] = cell_ids
            all_good = all_good and cell_ids == True
        return all_good
    
    def remove(self, obj):
        """Remove obj.
        """
        self.dirty = True
        buckets = self.buckets
        cell_ids = self.cell_ids
        if obj in cell_ids:
## Python 3 pukes
##            for cell_id in cell_ids[obj][:]:
            for cell_id in tuple(cell_ids[obj]):
## FIXED ... =P  problem was this line ^^^^ remove while iterating.
##
##  File "C:\cygwin\home\bw\devel\python\multifac\pyweek13\gamelib\gummworld2\spatialhash.py", line 67, in remove
##    if cell_id: buckets[cell_id].remove(obj)
##ValueError: list.remove(x): x not in list
                buckets[cell_id].remove(obj)
##superfluous...
##                cell_ids[obj].remove(cell_id)
##            if len(cell_ids[obj]) == 0:
##                del cell_ids[obj]
            del cell_ids[obj]
    
    def get_nearby_objects(self, obj):
        """Return a list of objects that share the same cells as obj.
        
        This method honors self.sort_key.
        """
        nearby_objs = []
        try:
            cell_ids = self.intersect_indices(obj.rect)
        except AttributeError:
            rect = self._get_rect_for_line(obj)
            cell_ids = self.intersect_indices(rect)
        buckets = self.buckets
        for cell_id in cell_ids:
            nearby_objs.extend(buckets[cell_id])
        nearby_objs = list(set(nearby_objs))
        if self.sort_key:
            nearby_objs.sort(key=self.sort_key)
        return nearby_objs
    
    def get_cell(self, cell_id):
        """Return the cell stored at bucket index cell_id.
        
        The returned cell is a list of objects. None is returned if a cell does
        not exist for cell_id.
        """
        try:
            return self.buckets[cell_id]
        except:
            return None
    
    def index(self, cell):
        """Return the bucket index of cell.
        
        Returns None if cell does not exist in buckets.
        
        Note that SpatialHash.buckets.index(cell) does *NOT* work because
        list.index() tests equality, not identity.
        """
        for i, c in enumerate(self.buckets):
            if c is cell:
                return i
    
    def index_at(self, x, y):
        """Return the cell_id of the cell that contains point (x,y).
        
        None is returned if point (x,y) is not in bounds.
        """
        cell_size = self.cell_size
        rect = self.rect
        idx = ((x - rect[0]) // cell_size) + ((y - rect[1]) // cell_size) * self.cols
        return int(idx) if -1 < idx < self.num_buckets else None
    
    def intersect_indices(self, rect):
        """Return list of cell ids that intersect rect.
        """
        # Not pretty, but these ugly optimizations shave 50% off run-time
        # versus function calls and attributes. This method is called by add(),
        # which gets called whenever an object moves.
        
        # return value
        cell_ids = {}
        
        # pre-calculate bounds
        left = rect[0]
        top = rect[1]
        right = left + rect[2]
        bottom = top + rect[3]
        wl, wt, wr, wb = self.bounds
        if left < wl:
            left = wl
        if top < wt:
            top = wt
        if right > wr:
            right = wr
        if bottom > wb:
            bottom = wb
        cell_size = self.cell_size
        
        # pre-calculate loop ranges
        lrange = range
        x_range = list(lrange(left, right, cell_size)) + [right]
        y_range = list(lrange(top, bottom, cell_size)) + [bottom]
        
        # misc speedups
        cols = self.cols
        
        for x in x_range:
            for y in y_range:
                cell_id = x // cell_size + y // cell_size * cols
                cell_ids[cell_id] = 1
        
#        return list(cell_ids)
        return cell_ids.keys()
    
    def intersect_objects(self, rect):
        """Return list of objects whose rects intersect rect.
        
        This method honors self.sort_key.
        """
        objs = {}
        colliderect = rect.colliderect
        rg = geometry.RectGeometry(*rect)
        for cell_id in self.intersect_indices(rect):
            for o in self.get_cell(cell_id):
                try:
                    if colliderect(o.rect):
                        try:
                            if o.collided(o, rg, True):
                                objs[o] = 1
                        except AttributeError:
                            objs[o] = 1
                except AttributeError:
                    try:
                        if o.collided(o, rg, True):
                            objs[o] = 1
                    except AttributeError:
                        pass
        objs = list(objs)
        if self.sort_key:
            objs.sort(key=self.sort_key)
        return objs
    
    def get_cell_grid(self, cell_id):
        """Return the (col,row) coordinate for cell id.
        """
        cols = self.cols
        x = cell_id // cols
        y = cell_id - x * cols
        return x, y
    
    def get_cell_pos(self, cell_id):
        """Return the world coordinates for topleft corner of cell.
        """
        x, y = self.get_cell_grid(cell_id)
        cell_size = self.cell_size
        rect = self.rect
        return x * cell_size + rect.left, y * cell_size + rect.top
    
    def collideany(self, obj):
        """Return True if obj collides with any other object, else False.
        """
        for other in self.get_nearby_objects(obj):
            if other is obj:
                continue
            try:
                if obj.rect.colliderect(other.rect):
                    try:
                        if obj.collided(obj, other, True):
                            return True
                    except AttributeError:
                            return True
            except AttributeError:
                try:
                    if obj.collided(obj, other, True):
                        return True
                except AttributeError:
                    pass
        return False
    
    def collide(self, obj):
        """Return list of objects that collide with obj.
        """
        collisions = []
        append = collisions.append
        for other in self.get_nearby_objects(obj):
            if other is obj:
                continue
            try:
                if obj.rect.colliderect(other.rect):
                    try:
                        if obj.collided(obj, other, True):
                            append(other)
                    except AttributeError:
                            append(other)
            except AttributeError:
                try:
                    if obj.collided(obj, other, True):
                        append(other)
                except AttributeError:
                    pass
        return collisions
    
    def collidealldict(self, rect=None):
        """Return dict of all collisions.
        
        If rect is specified, only the cells that intersect rect will be
        checked.
        
        The contents of the returned dict are: {obj : [other1,other2,...],...}
        """
        collisions = {}
        self.coll_tests = 0
        if rect:
            buckets = self.buckets
            cells = [buckets[i] for i in self.intersect_indices(rect)]
        else:
            cells = self.buckets
        tests = 0
        for cell in cells:
            for obj in cell:
                for other in cell:
                    if other is obj:
                        continue
                    tests += 1
                    try:
                        if obj.rect.colliderect(other.rect):
                            try:
                                if obj.collided(obj, other, True):
                                    try:
                                        collisions[obj].append(other)
                                    except KeyError:
                                        collisions[obj] = [other]
                            except AttributeError:
                                    try:
                                        collisions[obj].append(other)
                                    except KeyError:
                                        collisions[obj] = [other]
                    except AttributeError:
                        try:
                            if obj.collided(obj, other, True):
                                try:
                                    collisions[obj].append(other)
                                except KeyError:
                                    collisions[obj] = [other]
                        except AttributeError:
                            pass
        self.coll_tests = tests
        return collisions
    
    def collidealllist(self, rect=None):
        """Return list of all collisions.
        
        If rect is specified, only the cells that intersect rect will be
        checked.
        
        The contents of the returned list are: [(obj,other),...]
        """
        collisions = {}
        if rect:
            buckets = self.buckets
            cells = [buckets[i] for i in self.intersect_indices(rect)]
        else:
            cells = self.buckets
        tests = 0
        for cell in cells:
            for obj in cell:
                for other in cell:
                    if other is obj:
                        continue
                    tests += 1
                    try:
                        if obj.rect.colliderect(other.rect):
                            try:
                                if obj.collided(obj, other, True):
                                    collisions[(obj, other)] = 1
                            except AttributeError:
                                    collisions[(obj, other)] = 1
                    except AttributeError:
                        try:
                            if obj.collided(obj, other, True):
                                collisions[(obj, other)] = 1
                                collisions[(other, obj)] = 1
                        except AttributeError:
                            pass
        self.coll_tests = tests
        return collisions.keys()
    
    def collideallflatlist(self, rect=None):
        """Return flat list of all collisions.
        
        If rect is specified, only the cells that intersect rect will be
        checked.
        
        The contents of the returned list are: [obj1,other1,obj2,other2...]
        """
        collisions = []
        append = collisions.append
        if rect:
            buckets = self.buckets
            cells = [buckets[i] for i in self.intersect_indices(rect)]
        else:
            cells = self.buckets
        tests = 0
        for cell in cells:
            for obj in cell:
                for other in cell:
                    if other is obj:
                        continue
                    tests += 1
                    try:
                        if obj.rect.colliderect(other.rect):
                            try:
                                if obj.collided(obj, other, True):
                                    append(obj)
                                    append(other)
                            except AttributeError:
                                    append(obj)
                                    append(other)
                    except AttributeError:
                        try:
                            if obj.collided(obj, other, True):
                                append(obj)
                                append(other)
                        except AttributeError:
                            pass
        self.coll_tests = tests
        return collisions
    
    def clear(self):
        """Clear all objects.
        """
        self.dirty = True
        for cell in self.buckets:
            del cell[:]
    
    def iterobjects(self):
        """Returns a generator that iterates over all objects.
        
        Invoking a SpatialHash object as an iterator produces the same behavior
        as iterobjects().
        
        This method honors self.sort_key.
        """
        if self.sort_key:
            if self.dirty:
                self.sorted_objects[:] = sorted(
                    self.cell_ids, key=self.sort_key)
                self.dirty = False
            for obj in self.sorted_objects:
                yield obj
        else:
            for obj in self.cell_ids:
                yield obj
    
    def itercells(self):
        """Returns a generator that iterates over all cells.
        """
        for cell in self.buckets:
            yield cell
    
    # def _extended_collided(obj, other):
    #     """Deprecated - moved inline for speed
    #     """
    #     try:
    #         if obj.rect.colliderect(other.rect):
    #             try:
    #                 return obj.collided(obj, other, True)
    #             except AttributeError:
    #                     return True
    #         else:
    #             return False
    #     except AttributeError:
    #         try:
    #             return obj.collided(obj, other, True)
    #         except AttributeError:
    #             return False
    
    def _get_rect_for_line(self, obj):
        """Lines don't have a rect attribute. Use self._temp_rect to fudge it.
        """
        points = obj.points
        rect = self._temp_rect
        x1, y1 = points[0]
        x2, y2 = points[1]
        if x1 > x2:
            t = x1
            x1 = x2
            x2 = t
        if y1 > y2:
            t = y1
            y1 = y2
            y2 = t
        rect.topleft = x1, y1
        rect.width = x2 - x1
        rect.height = y2 - y1
        return rect
    
    def __iter__(self):
        """This method honors self.sort_key."""
        if self.sort_key:
            if self.dirty:
                self.sorted_objects[:] = sorted(self.cell_ids, key=self.sort_key)
                self.dirty = False
            for obj in self.sorted_objects:
                yield obj
        else:
            for obj in self.cell_ids:
                yield obj
    
    def __contains__(self, obj):
        return obj in self.cell_ids
    
    def __len__(self):
        #return len(self.objects)
        return len(self.cell_ids)
    
    def __str__(self):
        # return '<%s(%s,%s)>' % (
        #     self.__class__.__name__,
        #     str(self.rect),
        #     str(self.cell_size),
        # )
        return '<{}({},{})>'.format(self.__class__.__name__, str(self.rect), str(self.cell_size))

    def __repr(self):
        return self.__str__()


# Commented because variables are causing 'shadows name from outer scope' warnings in PyCharm.
# if __name__ == '__main__':
#     class Obj(object):
#         def __init__(self, x, y):
#             self.rect = Rect(x,y,4,4)
#         def __str__(self):
#             return '<%s(%d,%d)>' % (
#                 self.__class__.__name__,
#                 self.rect.x,
#                 self.rect.y,
#             )
#         def __repr__(self):
#             return self.__str__()
#     pygame.init()
#     world_rect = Rect(0,0,180,180)
#     print('World rect: {0}'.format(world_rect))
#     cell_size = 30
#     shash = SpatialHash(world_rect, cell_size)
#     print('SpatialHash: {0} {1:d} {2:d}'.format(
#         shash, shash.rows, shash.cols))
#     print('{0} {1} {2}'.format(shash.rows, shash.cols, len(shash.buckets)))
#     o = Obj(15,15)
#     shash.add(o)
#     assert o in shash
#     assert shash.collideany(o) == False
#     shash.add(Obj(16,15))
#     shash.add(Obj(25,15))
#     shash.add(Obj(30,15))
#     shash.add(Obj(40,15))
#     shash.add(Obj(15,40))
#     assert shash.collideany(o)
#     print(shash.collide(o))
#     print(shash.collidealldict())
#     print(shash.collidealllist())
#     print(shash.intersect_indices(Rect(0,0,cell_size,cell_size)))
#     print(shash.intersect_indices(Rect(0,30,cell_size,cell_size)))
#     print('Objects 1 (__iter__):')
#     for obj in shash:
#         print(obj)
#     print('Objects 2 (iterobjects):')
#     for obj in shash.iterobjects():
#         print(obj)
#     print('Objects 3 (objects):')
#     for obj in shash.objects:
#         print(obj)
#     print('Cell position:')
#     for i in range(len(shash.buckets)):
#         print('{0} {1} {2}'.format(
#             i, shash.get_cell_grid(i), shash.get_cell_pos(i)))
#     print('Nearby objects:')
#     print('  Reference: {0} {1}'.format(o, shash.cell_ids[o]))
#     for obj in shash.get_nearby_objects(o):
#         print('  nearby: {0} {1}'.format(obj, shash.cell_ids[obj]))
#
#     screen = pygame.display.set_mode(world_rect.size)
#     draw_line = pygame.draw.line
#     draw_rect = pygame.draw.rect
#     color = pygame.Color('darkgrey')
#     left,right,top,bottom = world_rect.left,world_rect.right,world_rect.top,world_rect.bottom
#     fill_rect = Rect(0,0,shash.cell_size,shash.cell_size)
#     while 1:
#         pygame.event.clear()
#         screen.fill((0,0,0))
#         minx = -1
#         miny = -1
#         for cell_id,cell in enumerate(shash.itercells()):
#             x,y = shash.get_cell_pos(cell_id)
#             if x > minx:
#                 minx = x
#                 p1 = x,top
#                 p2 = x,bottom
#                 draw_line(screen, color, p1, p2)
#             if y > miny:
#                 miny = y
#                 p1 = left,y
#                 p2 = right,y
#                 draw_line(screen, color, p1, p2)
#         x,y = pygame.mouse.get_pos()
#         row,col = shash.get_cell_grid(shash.index_at(x,y))
#         fill_rect.topleft = col*shash.cell_size,row*shash.cell_size
#         screen.fill((0,255,255), fill_rect)
#         for o in shash.objects:
#             draw_rect(screen, (0,0,255), o.rect)
#         pygame.display.flip()
