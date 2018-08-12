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

"""basicmaprenderer.py - Basic Map Renderer module for Gummworld2.

Defines the BasicMapRenderer, which serves an intermediate batch of tiles
for efficient rendering. This class is intended to be used instead of
BasicMap's collapse() and reduce() functions. The renderer is compatible with
a collapsed map; it is simply offered as a replacement that is significantly
easier to use.

LAYERED MAPS

On maps with many layers and images with alpha the gain is quite significant.

There are two ways to use the renderer: managing background layers only, and
managing dynamic layers.

MANAGING BACKGROUND LAYERS ONLY

In this case background layers are static, so very little care is needed. Here
is an example game loop:

    def update(self, dt):
        if self.movex or self.movey:
            State.camera.position += self.movex,self.movey
        State.camera.update()
        self.renderer.set_rect(center=State.camera.rect.center)

    def draw(self, dt):
        State.screen.clear()
        self.renderer.draw_tiles()
        self.draw_my_foreground()
        State.screen.flip()

MANAGING DYNAMIC LAYERS

In this case dynamic layers have sprites or tiles being moved, added, and
removed. The renderer needs to be told when these events occur. This is done
via the renderer's set_dirty() method. Here is an example game loop:

    def update(self, dt):
        if self.movex or self.movey:
            State.camera.position += self.movex,self.movey
        State.camera.update()

    def draw(self, interp):
        State.screen.clear()
        
        renderer = self.renderer
        
        # If panning, mark the renderer's tiles dirty where avatar is.
        panning = False
        camera = State.camera
        camera_rect = camera.rect
        dirty_rect = self.dirty_rect
        camera_center = camera_rect.center
        if camera.target.rect.center != camera_center:
            dirty_rect.center = camera_center
            renderer.set_dirty(dirty_rect)
            panning = True
        
        # Set render's rect and draw the screen.
        renderer.set_rect(center=camera_center)
        renderer.draw_tiles()
        
        # Must mark dirty rect before next call to draw(), otherwise avatar
        # leaves little artifacts behind.
        if panning:
            renderer.set_dirty(dirty_rect)
        
        State.screen.flip()

WHEN CAMERA TARGET IS THE AVATAR

It is normal to make the avatar the camera target so that the camera tracks
the avatar's movement. If the avatar is inserted into a map layer for the
renderer to draw, there are two issues that need to be dealt with:
interpolation jitters, and tile order.

INTERPOLATION JITTERS

The camera's interpolation of the map tiles causes the avatar to jitter. The
renderer needs to be told to defeat interpolation. This is done by setting the
camera target's anti_interp attribute, e.g.:

    class Avatar:
    def __init__(self):
        self.anti_interp = True

TILE ORDER

If tile order in a layer is critical to proper rendering, the renderer must be
told to sort the layer. Tile order is normally critical in 2.5D
implementations. This is done by setting the layer's sort_key attribute, e.g.:

    map = TiledMap('my backyard.tmx')
    map.layers[i].sort_key = lambda obj: obj.rect.bottom

GARBAGE CLEANUP

The class attribute DEFAULT_LIFESPAN is the number of checks to perform
before retiring a tile that has not been displayed recently. Consider this a
crudely tunable garbage collector.

MESSY EDGES

If an occasional black band appears at the edge of the display while 
scrolling, increase the value of max_scroll_speed to the value of the
largest step (x or y) in use. This value can be changed situationally,
on the fly, without significant overhead. This issue is due to interpolation
of large scroll steps.
"""


__version__ = '$Id: basicmaprenderer.py 433 2014-03-21 03:39:35Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'


__all__ = ['BasicMapRenderer', 'BasicMapRendererTile']


import sys

if sys.version_info[0] == 3:
    # This is dirty but range can be expensive with large sequences in
    # Python 2.
    xrange = range


import pygame
from pygame.locals import *

from gummworld2 import State, BasicMap, Vec2d


class BasicMapRenderer(object):
    
    DEFAULT_LIFESPAN = 30 * 2  # ticks * calls to get_tiles()
    
    _allowed_rect = (
        'x', 'y', 'left', 'right', 'top', 'bottom',
        'center', 'midleft', 'midright', 'midtop', 'midbottom',
        'topleft', 'topright', 'bottomleft', 'bottomright',
    )
    
    def __init__(self, basic_map, tile_size=0, max_scroll_speed=10):
        self._basic_map = basic_map
        self._rect = Rect(State.camera.view.rect)
        self._max_scroll_speed = max_scroll_speed
        
        self._tiles = {}
        self._visible_tiles = []
        
        self._view_count = 0
        self._lifespan = self.DEFAULT_LIFESPAN
        self._examine_queue = []
        self._dead = []
        self.dirty_rects = []
        
        self.tile_size = tile_size
        
        self.get_tiles()
    
    def get_rect(self):
        return Rect(self._rect)

    def set_rect(self, **kwargs):
        """set the world location of the renderer's view rect"""
        ## may be an opportunity here for a memoization performance gain to
        ## keep tiles if the move does not select a new region
        del self._visible_tiles[:]
        for k in kwargs:
            if k not in self._allowed_rect:
                raise pygame.error('rect attribute not permitted: %s' % (k,))
            setattr(self._rect, k, kwargs[k])
        self.get_tiles()
        del self.dirty_rects[:]
    
    @property
    def max_scroll_speed(self):
        return self._max_scroll_speed

    @max_scroll_speed.setter
    def max_scroll_speed(self, val):
        assert isinstance(val, int)
        self._max_scroll_speed = val

    @property
    def lifespan(self):
        return self._lifespan

    @lifespan.setter
    def lifespan(self, val):
        """set a new lifespan on tiles"""
        self._lifespan = val

    @property
    def tile_size(self):
        return self._tile_size

    @tile_size.setter
    def tile_size(self, val):
        """set a new tile size"""
        assert isinstance(val, int)
        if val <= 0:
            # change from 4 to 6 for better FPS while scrolling, which activity
            # adds newly rendered tiles on the fly
            val = self._rect.width // 6
        self._tile_size = val
        self.clear()
        self.get_tiles()

    @property
    def basic_map(self):
        return self._basic_map

    @basic_map.setter
    def basic_map(self, val):
        """register a new BasicMap"""
        assert isinstance(val, BasicMap)
        self._basic_map = val
        self.clear()
        self.get_tiles()
    
    def set_dirty(self, *areas):
        """specify areas to re-render
        
        The areas argument must be one or more pygame.Rect.
        
        Marking areas dirty is necessary only if the underlying BasicMap
        tiles are procedurally modified during runtime. Though it involves
        some management, it is potentially much more efficient than
        triggering the entire view be recreated.
        """
        tiles = self._tiles
        for rect in areas:
            for tile in tuple(tiles.values()):
                if rect.colliderect(tile.rect):
                    self.dirty_rects.append(tile.rect)
                    del tiles[tile.idx]
        self.get_tiles()
    
    def get_tiles(self):
        """call once per tick to calculate visible tiles
        
        The constructor does this automatically, and it is done each time
        set_rect() is called. It may be necessary to call get_tiles()
        manually depending on the implementation; for example, if the
        renderer object is created before the map is loaded.
        """
        visible_tiles = self._visible_tiles
        if visible_tiles:
            return
        
        self._view_count += 1
        self._age_tiles()
        stamp = self._view_count
        
        speed = self._max_scroll_speed * 2
        X, Y, W, H = self._rect.inflate(speed, speed)
        SIZE = self._tile_size
        X = X // SIZE * SIZE
        Y = Y // SIZE * SIZE
        TILES = self._tiles
        get_tile = TILES.get
        for x in range(X, X + W + SIZE, SIZE):
            for y in range(Y, Y + H + SIZE, SIZE):
                idx = x, y
                if idx not in TILES:
                    tile = BasicMapRendererTile(idx, SIZE, self)
                    TILES[idx] = tile
                else:
                    tile = get_tile(idx)
                tile.stamp = stamp
                visible_tiles.append(tile)
    
    def draw_tiles(self):
        """draw the visible tiles on the screen"""
        cam_rect = State.camera.rect
        self._rect.center = cam_rect.center
        blit = State.camera.surface.blit
        view_rect = self._rect
        colliderect = view_rect.colliderect
        x, y = cam_rect.topleft
        for tile in self._visible_tiles:
            r = tile.rect
            im = tile.image
            if im and colliderect(r):
                blit(im, r.move(-x, -y))
    
    def _age_tiles(self):
        """weed out aged tiles nicely"""
        queue = self._examine_queue
        tiles = self._tiles
        if not queue:
            queue[:] = list(tiles.values())
        stamp = self._view_count
        dead = self._dead
        lifespan = self._lifespan
        i = 0
        while queue:
            i += 1
            if i > 30:
                # performance throttle: only do 30 per check
                break
            tile = queue.pop(0)
            if stamp - tile.stamp > lifespan:
                dead.append(tile)
        for tile in dead:
            try:
                del tiles[tile.idx]
            except KeyError:
                pass
        del dead[:]
    
    def clear(self):
        """clear all tile caches"""
        self._tiles.clear()
        del self._visible_tiles[:]
        del self._examine_queue[:]
        del self._dead[:]
        del self.dirty_rects[:]


class BasicMapRendererTile(object):
    
    def __init__(self, idx, size, renderer):
        self.idx = idx
        self.renderer = renderer
        dim = (size, size)
        self.image = pygame.Surface(dim)
        self.rect = self.image.get_rect(topleft=idx, size=dim)
        
        blit = self.image.blit

        map_ = State.map
        camera = State.camera
        camera_rect = camera.rect
        camera_rect_center = camera_rect.center
        cx, cy = self_rect_topleft = self.rect.topleft
        visible_cell_ids = _get_visible_cell_ids(camera, map_, self.rect)
        visible_objects = _get_objects_in_cell_ids(map_, visible_cell_ids)
        for sprites in visible_objects:
            for sprite in sprites:
                im = sprite.image
                if im:
                    if getattr(sprite, 'anti_interp', False):
                        sprite_rect = sprite.rect
                        t = Vec2d(sprite_rect.center) - camera_rect_center
                        anti_interp = -(self_rect_topleft + t)
                        blit(im, sprite_rect.move(anti_interp))
                    else:
                        sx, sy = sprite.rect.topleft
                        blit(im, (sx - cx, sy - cy))


# The following functions
#   _get_visible_cell_ids
#   _get_objects_in_cell_ids
# are similar to the functions of the same name in gummworld2.toolkit,
# except that they operate on a query_rect instead of the camera.
#
# These functions assist a BasicMapRendererTile in constructing itself.

def _get_visible_cell_ids(camera, map_, query_rect):
    empty_list = []
    cell_ids = []
    for layer in map_.layers:
        if layer.visible:
            cell_ids.append(layer.objects.intersect_indices(query_rect))
        else:
            cell_ids.append(empty_list)
    return cell_ids


def _get_objects_in_cell_ids(map_, cell_ids_per_layer):
    objects_per_layer = []
    for layeri, cell_ids in enumerate(cell_ids_per_layer):
        layer = map_.layers[layeri]
        if not layer.visible:
            continue
        get_cell = layer.objects.get_cell
        objects = set()
        objects_update = objects.update
        for cell_id in cell_ids:
            objects_update(get_cell(cell_id))
        objects = list(objects)
        sort_key = layer.objects.sort_key
        if sort_key:
            objects.sort(key=sort_key)
        objects_per_layer.append(objects)
    return objects_per_layer
