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


"""ui.py - User Interface module for Gummworld2.

Currently there is only HUD. And some dynamic stats classes with timers for
callback.
"""

__version__ = '$Id: ui.py 407 2013-08-12 15:11:30Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'

__all__ = ['hud_font', 'hud_alpha', 'HUD', 'Stat', 'Statf']


import pygame
from pygame.locals import Color, RLEACCEL

if __name__ == '__main__':
    import paths
from gummworld2 import data, State


pygame.init()
hud_font = pygame.font.Font(data.filepath('font', 'Vera.ttf'), 10)
hud_alpha = 208
text_color = Color('yellow')


class HUD(pygame.sprite.OrderedUpdates):
    
    def __init__(self):
        super(HUD, self).__init__()
        self.stats = {}
        self.ordered = []
        self.top = 5
        self.font_height = hud_font.get_height()
#        self.y = lambda n: self.top + self.font_height * n
        self.x = State.screen.rect.x + 5
        self.i = 0
        self._visible = True
    
    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, boolean):
        self._visible = boolean
    
    @property
    def bottom(self):
        return self.top + sum([s.font.size('W')[1] for s in self])

    def next_pos(self):
        self.i += 1
        return self.x, self.bottom

    def add(self, *args):
        """args: name, stat"""
        if args:
            name, stat = args[0:2]
            self.stats[name] = stat
            super(HUD, self).add(stat)
    
    def remove(self, *sprites):
        """remove sprites by name or sprite object"""
        for sprite in sprites:
            if isinstance(sprite, str):
                name = sprite
                sprite = self.stats[sprite]
                del self.stats[name]
            else:
                for key, value in self.stats.items():
                    if value is sprite:
                        del self.stats[key]
            super(HUD, self).remove(sprite)

    def update(self, dt):
        for stat in self.stats.values():
            stat.update(dt)

    def draw(self, dt=0, surface=None):
        if not self.visible:
            return
        if surface is None:
            super(HUD, self).draw(State.camera.surface)
        else:
            super(HUD, self).draw(surface)


class Stat(pygame.sprite.Sprite):
    """a HUD stat with plain string

    pos: x, y screen position
    text: text value of this HUD item
    callback: a callable that takes no args and returns a string to replace the current value
    interval: time between callbacks in seconds
    font: custom font for this HUD item
    """
    
    def __init__(self, pos, text=None, callback=None, interval=2.0, font=hud_font):
        pygame.sprite.Sprite.__init__(self)
        self.font = font
        self.text = None
        self.callback = callback
        self.interval = interval
        self.time_left = 0
        if text is not None:
            self.set_value(text)
        elif callback:
            self.update(0)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, dt):
        if self.callback:
            self.time_left -= dt
            if self.time_left <= 0.0:
                value = self.callback()
                if value is not None:
                    self.set_value(value)
                self.time_left = self.interval
    
    def set_value(self, text):
        if isinstance(text, str) and text != self.text:
            self.text = text
            self.image = self.font.render(text, True, text_color)
            self.image.set_alpha(hud_alpha)


class Statf(pygame.sprite.Sprite):
    """a HUD stat with formatted string

    pos: x, y screen position
    fmt: new-style format string (i.e. '{}'.format())
    value: initial sequence of values used by string format
    callback: a callable that takes no args and returns a sequence usable by string format
    interval: time between callbacks in seconds
    font: custom font for this HUD item
    """
    
    def __init__(self, pos, fmt, value=None, callback=None, interval=2.0, font=hud_font):
        pygame.sprite.Sprite.__init__(self)
        self.font = font
        self.fmt = fmt
        self.value = None
        self.callback = callback
        self.interval = interval
        self.time_left = 0
        if value is not None:
            self.set_value(value)
        elif callback:
            self.update(0)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def update(self, dt):
        if self.callback:
            self.time_left -= dt
            if self.time_left <= 0.0:
                seq = self.callback()
                if seq is not None:
                    self.set_value(seq)
                self.time_left = self.interval
    
    def set_value(self, seq):
        if seq and seq != self.value:
            self.value = seq
            self.image = self.font.render(self.fmt.format(*seq), True, text_color)
            self.image.set_alpha(hud_alpha)

if __name__ == '__main__':
    from gummworld2 import Screen, GameClock
    State.screen = Screen((600, 600))
    State.clock = GameClock(max_fps=30)
    left = 20
    top = 20
    height = hud_font.get_height()
    State.hud = HUD()
    y = lambda n: top + height * n
    State.hud.add('stat1', Stat((left, y(0)), 'Stat 1'))
    State.hud.add('time', Statf((left, y(1)), 'Time {:.0f}', callback=lambda: State.clock.get_ticks(), interval=.1))
    State.hud.add('fps', Statf((left, y(2)), 'FPS {:.0f}', callback=lambda: round(State.clock.fps)))
    State.clock.schedule_interval(State.hud.update, 1.0)
    while True:
        State.clock.tick()
        State.screen.clear()
        State.hud.draw(surface=State.screen.surface)
        State.screen.flip()
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                quit()
