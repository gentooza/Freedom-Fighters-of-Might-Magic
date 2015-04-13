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

"""geometry.py - Geometry module for Gummworld2.

Geometry classes and functions.
"""

__version__ = '$Id: geometry.py 432 2013-09-07 03:43:04Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'

__all__ = [
    'Ellipse', 'Diamond', 'LineGeometry', 'RectGeometry', 'CircleGeometry', 'PolyGeometry',
    'angle_of', 'distance', 'interpolant_of_line', 'point_on_circumference', 'step_toward_point', 'point_in_poly',
    'circle_collided_other', 'rect_collided_other', 'line_collided_other', 'poly_collided_other',
    'circle_intersects_circle', 'circle_intersects_line', 'circle_intersects_rect', 'circle_intersects_poly',
    'line_intersects_line', 'lines_intersect_lines', 'line_intersects_rect', 'line_intersects_poly',
    'poly_intersects_rect', 'poly_intersects_poly',
    'points_to_lines', 'rect_to_lines',
]


from math import atan2, cos, sin, sqrt, pi, radians
import sys

if sys.version_info[0] == 3:
    from functools import reduce

import pygame

from .vec2d import Vec2d


class Ellipse(object):
    
    def __init__(self, origin, radius_x, radius_y):
        """Construct an instance of Ellipse.
        
        The origin argument is a sequence of two numbers representing the origin
        (x,y).
        
        The radius_x argument is a number representing the radius along x-axis.
        
        The radius_y argument is a number representing the radius along y-axis.
        """
        self.origin = origin
        self.radius_x = radius_x
        self.radius_y = radius_y
        
        self._points = None
        self._dirty = True
    
    @property
    def origin(self):
        """Set or get origin."""
        return self._origin

    @origin.setter
    def origin(self, val):
        self._origin = val
        self._dirty = True
        
    @property
    def radius_y(self):
        """Set or get radius_y."""
        return self._radius_y

    @radius_y.setter
    def radius_y(self, val):
        self._radius_y = val
        self._dirty = True
        
    @property
    def radius_x(self):
        """Set or get radius_x."""
        return self._radius_x

    @radius_x.setter
    def radius_x(self, val):
        self._radius_x = val
        self._dirty = True
        
    def draw(self, surface, color, arcs=360):
        """Draw an ellipse on a pygame surface in the specified color.
        
        The surface argument is the target pygame surface.
        
        The color argument is the pygame color to draw in.
        
        The arcs argument is the number of points in the circumference to draw;
        normally 360 or 720 will suffice. More than 720 will draw many duplicate
        pixels.
        """
        if not self._dirty:
            points = self._points
        else:
            points = self.plot(arcs)
        pygame.draw.lines(surface, color, True,
            [(int(round(x)), int(round(y))) for x, y in points])
        
    def plot(self, arcs=360):
        """Plot the circumference of an ellipse and return the points in a list.
        
        The arcs argument is the number of points in the circumference to
        generate; normally 360 or 720 will suffice. More than 720 will result in
        many duplicate points.
        
        The list that is returned is a sequence of (x,y) tuples suitable for
        use with pygame.draw.lines().
        """
        if not self._dirty:
            return list(self._points)
        else:
            circumference = []
            arcs = int(round(arcs))
            for n in xrange(0, arcs):
                angle = 360.0 * n / arcs
                x, y = self.point(angle)
                circumference.append((x, y))
            self._points = circumference
            self._dirty = False
            return circumference
        
    def point(self, angle):
        """Plot a point on the circumference of an ellipse at the specified angle.
        The point is returned as an (x,y) tuple.
        
        The angle argument is the angle in degrees from the origin. The angle 0
        and 360 are oriented at the top of the screen, and increase clockwise.
        """
        # angle-90 converts screen space to math function space
        rad = radians(angle - 90)
        x = self.radius_x * cos(rad)
        y = self.radius_y * sin(rad)
        ox, oy = self.origin
        return x + ox, y + oy


class Diamond(pygame.Rect):
    
    def __init__(self, *args):
        """Diamond(left, top, width, height) : Rect
        Diamond((left, top), (width, height)) : Rect
        Diamond(object) : Rect
        
        Construct it like a pygame.Rect. All the Rect attributes and methods
        are available.
        
        In addition, there are read-only attributes for:
            *   Individual corners: top_center, right_center, bottom_center, and
                left_center.
            *   Individual edges: side_a, side_b, side_c, side_d.
            *   All corners as a tuple of coordinates: corners.
            *   All edges as a tuple of line segments: edges.
        """
        super(Diamond, self).__init__(*args)
    
    @property
    def top_center(self):
        return self.centerx, self.top

    @property
    def right_center(self):
        return self.right, self.centery

    @property
    def bottom_center(self):
        return self.centerx, self.bottom

    @property
    def left_center(self):
        return self.left, self.centery
    
    @property
    def side_a(self):
        return self.top_center, self.right_center

    @property
    def side_b(self):
        return self.right_center, self.bottom_center

    @property
    def side_c(self):
        return self.bottom_center, self.left_center

    @property
    def side_d(self):
        return self.left_center, self.top_center

    @property
    def corners(self):
        return self.top_center, self.right_center, self.bottom_center, self.left_center

    @property
    def edges(self):
        return self.side_a, self.side_b, self.side_c, self.side_d


def angle_of(origin, end_point):
    """Calculate the angle between the vector defined by end points (origin,point)
    and the Y axis. All input and output values are in terms of pygame screen
    space. Returns degrees as a float.
    
    The origin argument is a sequence of two numbers representing the origin
    point.
    
    The point argument is a sequence of two numbers representing the end point.
    
    The angle 0 and 360 are oriented at the top of the screen, and increase
    clockwise.
    """
    x1, y1 = origin
    x2, y2 = end_point
    return (atan2(y2 - y1, x2 - x1) * 180.0 / pi + 90.0) % 360.0


def distance(a, b):
    """Calculate the distance between points a and b. Returns distance as a float.
    
    The a argument is a sequence representing one end point (x1,y1).
    
    The b argument is a sequence representing the other end point (x2,y2).
    """
    x1, y1 = a
    x2, y2 = b
    diffx = x1 - x2
    diffy = y1 - y2
    return (diffx * diffx + diffy * diffy) ** 0.5


def interpolant_of_line(mag, p1, p2):
    """Find the point at magnitude mag along a line."""
    x1, y1 = p1
    x2, y2 = p2
    dx = (x2 - x1) * mag
    dy = (y2 - y1) * mag
    return x1 + dx, y1 + dy


def point_on_circumference(center, radius, degrees_):
    """Calculate the point on the circumference of a circle defined by center and
    radius along the given angle. Returns a tuple (x,y).
    
    The center argument is a representing the origin of the circle.
    
    The radius argument is a number representing the length of the radius.
    
    The degrees_ argument is a number representing the angle of radius from
    origin. The angles 0 and 360 are at the top of the screen, with values
    increasing clockwise.
    """
    radians_ = radians(degrees_ - 90)
    x = center[0] + radius * cos(radians_)
    y = center[1] + radius * sin(radians_)
    return x, y


def step_toward_point(p1, p2, distance):
    """Calculate the point at a given distance along the line with end points
    (x1,y1) and (x2,y2).
    
    This function is about twice as fast as the combination angle_of() and
    point_on_circumference().
    
    The (x1,y1) argument is the origin.
    
    The (x2,y2) argument is the destination.
    
    The distance argument is the size of the step, or speed.
    """
    x1, y1 = p1
    x2, y2 = p2
    line = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    step = line / distance
    new_x = x1 + (x2 - x1) / step
    new_y = y1 + (y2 - y1) / step
    return new_x, new_y


def point_in_poly(point, poly):
    """Point vs polygon collision test.
    
    Poly is assumed to be a sequence of points, length >= 3, with no duplicate
    points. Winding is not a factor.
    """
    x, y = point
    inside = False
    
    p1x, p1y = poly[0]
    for p2x, p2y in poly[1:] + [poly[0]]:
        miny = p1y if p1y < p2y else p2y
        if y > miny:
            maxy = p1y if p1y > p2y else p2y
            if y <= maxy:
                maxx = p1x if p1x > p2x else p2x
                if x <= maxx:
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def circle_collided_other(self, other, rect_pre_tested=None):
    """Return results of collision test between a circle and other geometry.
    
    The *_collided_other() functions provide a convenient means to test
    disparate geometries for collision. The logic considers containment to be
    a collision. The tests do not check for the "self is other" condition.
    
    self is a circle, it must have origin and radius attrs.
    
    If other does not have a collided attr, then a circle-vs-rect result is
    returned.
    
    Otherwise...
    
    other must have attr collided. collided must be a staticmethod
    *_collided_other function or a custom function in that form. If collided is
    not one of the *_collided_other functions, other's collided function will
    be called passing arguments other and self in that order.
    
    other's collided attr dictates the kind of self-vs-other collision test. The
    builtin collision tests are:
    
        1.  If other.collided is circle_collided_other, other is assumed to be a
            circle with origin and radius attrs.
        2.  If other.collided is rect_collided_other, other is assumed to be a
            rect with a rect attr.
        3.  If other.collided is poly_collided_other, other is assumed to be a
            poly with a points attr.
        4.  If other.collided is line_collided_other, other is assumed to be a
            line with an end_points attr.
    
    The fall-through action is to call other.collided(other, self), which is
    assumed to be a custom staticmethod function.
    
    Here is an example minimal class and usage:
        
        class CircleGeom(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
            collided = staticmethod(circle_collided_other)
        
        circle = CircleGeom(origin=(300,300), radius=25)
        circle.collide(circle, other_poly)
    """
    origin = self.origin
    radius = self.radius
    if not hasattr(other, 'collided'):
#        return circle_intersects_rect(
#        origin, radius, rect_to_lines(other.rect))
        return circle_intersects_rect(origin, radius, other.rect)
    
    other_collided = other.collided
    if other_collided is circle_collided_other:
        return circle_intersects_circle(origin, radius, other.origin, other.radius)
    elif other_collided is rect_collided_other:
        rect = other.rect
        if circle_intersects_rect(origin, radius, rect):
            return True
        return rect.collidepoint(origin) == 1
    elif other_collided is poly_collided_other:
        points = other.points
        if circle_intersects_poly(origin, radius, points):
            return True
        return point_in_poly(origin, points)
    elif other_collided is line_collided_other:
        return circle_intersects_line(origin, radius, other.end_points)
    
    return other_collided(other, self)


def rect_collided_other(self, other, rect_pre_tested=None):
    """Return results of collision test between a rect and other geometry.
    
    self is a rect, it must have a rect attr.
    
    See circle_collided_other description for other details.
    """
    rect = self.rect
    if not hasattr(other, 'collided'):
        if rect_pre_tested is not None:
            return rect_pre_tested
        else:
            return rect.colliderect(other.rect) == True
    
    other_collided = other.collided
    if other_collided is circle_collided_other:
        origin = other.origin
        radius = other.radius
        if circle_intersects_rect(origin, radius, rect):
            return True
        return rect.collidepoint(origin) == 1
    elif other_collided is rect_collided_other:
        if rect_pre_tested is not None:
            return rect_pre_tested
        else:
            return rect.colliderect(other.rect) == 1
    elif other_collided is poly_collided_other:
        points = other.points
        if len(lines_intersect_lines(rect_to_lines(rect), points_to_lines(points))):
            return True
        if rect.collidepoint(points[0]):
            return True
        if point_in_poly(rect.center, points):
            return True
        return False
    elif other_collided is line_collided_other:
        end_points = other.end_points
        return len(line_intersects_rect(end_points, rect)) > 0 or \
            rect.collidepoint(end_points[0]) == True or \
            rect.collidepoint(end_points[1]) == True
    
    return other_collided(other, self)


def line_collided_other(self, other, rect_pre_tested=None):
    """Return results of collision test between a line and other geometry.
    
    self is a line, it must have an end_points attr.
    
    See circle_collided_other description for other details.
    """
    if not hasattr(other, 'collided'):
        return line_intersects_rect(self.end_points, other.rect)
    
    other_collided = other.collided
    if other_collided is circle_collided_other:
        return circle_intersects_line(other.origin, other.radius, self.end_points)
    elif other_collided is rect_collided_other:
        end_points = self.end_points
        rect = other.rect
        p1, p2 = end_points
        return len(line_intersects_rect(end_points, rect)) > 0 or \
            rect.collidepoint(p1) == True or rect.collidepoint(p2) == True
    elif other_collided is poly_collided_other:
        end_points = self.end_points
        points = other.points
        if len(line_intersects_poly(end_points, points)) > 0:
            return True
        if point_in_poly(end_points[0], points):
            return True
        return False
    elif other_collided is line_collided_other:
        return len(line_intersects_line(self.end_points, other.end_points)) > 0
    
    return other_collided(other, self)


def poly_collided_other(self, other, rect_pre_tested=None):
    """Return results of collision test between a poly and other geometry.
    
    self is a poly, it must have a points attr.
    
    See circle_collided_other description for other details.
    """
    if not hasattr(other, 'collided'):
        return poly_intersects_rect(self.points, other.rect)
    
    other_collided = other.collided
    if other_collided is circle_collided_other:
        points = self.points
        origin = other.origin
        radius = other.radius
        if circle_intersects_poly(origin, radius, points):
            return True
        return point_in_poly(origin, points)
    elif other_collided is rect_collided_other:
        points = self.points
        rect = other.rect
        if len(lines_intersect_lines(points_to_lines(points), rect_to_lines(rect))) > 0:
            return True
        if rect.collidepoint(points[0]):
            return True
        if point_in_poly(rect.center, points):
            return True
        return False
    elif other_collided is poly_collided_other:
        self_points = self.points
        other_points = other.points
        if poly_intersects_poly(self_points, other_points):
            return True
        if point_in_poly(self_points[0], other_points):
            return True
        if point_in_poly(other_points[0], self_points):
            return True
        return False
    elif other_collided is line_collided_other:
        points = self.points
        end_points = other.end_points
        if len(line_intersects_poly(end_points, points)) > 0:
            return True
        if point_in_poly(end_points[0], points):
            return True
        return False
    
    return other_collided(other, self)


class LineGeometry(object):
    
    def __init__(self, x1, y1, x2, y2, position=None):
        super(LineGeometry, self).__init__()
        self._p1 = Vec2d(x1, y1)
        self._p2 = Vec2d(x2, y2)
        if position is not None:
            self.position = position
    
    def getpoints(self):
        return tuple(self._p1), tuple(self._p2)

    def setpoints(self, endpoints):
        """set end points of line
        line.points = x1,y1,x2,y2
        line.points = (x1,y1),(x2,y2)
        """
        if len(endpoints) == 4:
            self._p1[:] = endpoints[0:2]
            self._p2[:] = endpoints[2:4]
        elif len(endpoints) == 2:
            self._p1[:] = endpoints[0]
            self._p2[:] = endpoints[1]
        else:
            raise ValueError('{0}.points: endpoints={1}'.format(self.__class__.__name__, endpoints))
    points = property(getpoints, setpoints)
    
    def getend_points(self):
        return self._p1[:], self._p2[:]
    end_points = property(getend_points)
    
    ## entity's collided, static method used by QuadTree callback
    collided = staticmethod(line_collided_other)
    
    def getposition(self):
        """GOTCHA: Something like "line_geom.position.x += 1" will not do what
        you expect. That operation does not update the line instance variable.
        Instead use "line_geom.position += (1,0)".
        """
        return self._center

    def setposition(self, val):
        x = val[0]
        y = val[1]
        cx, cy = self._center
        dx = x - cx
        dy = y - cy
        #
        p1 = self._p1
        p1[0] += dx
        p1[1] += dy
        #
        p2 = self._p2
        p2[0] += dx
        p2[1] += dy
    position = property(getposition, setposition)
    
    def _getcenter(self):
        p1 = self._p1
        x1 = p1[0]
        y1 = p1[1]
        #
        p2 = self._p2
        x2 = p2[0]
        y2 = p2[1]
        #
        cx = x1 + (x2 - x1) / 2
        cy = y1 + (y2 - y1) / 2
        return Vec2d(cx, cy)
    _center = property(_getcenter)
    
    def getp1(self):
        return self._p1[:]

    def setp1(self, xorxy, y=None):
        if y is None:
            self._p1[:] = xorxy
        else:
            self._p1[:] = xorxy, y
    p1 = property(getp1, setp1)
    
    def getp2(self):
        return self._p2[:]

    def setp2(self, xorxy, y=None):
        if y is None:
            self._p2[:] = xorxy
        else:
            self._p2[:] = xorxy, y
    p2 = property(getp2, setp2)
    
    def getx1(self):
        return self._p1[0]

    def setx1(self, val):
        self._p1[0] = val
    x1 = property(getx1, setx1)
    
    def gety1(self):
        return self._p1[1]

    def sety1(self, val):
        self._p1[1] = val
    y1 = property(gety1, sety1)
    
    def getx2(self):
        return self._p2[0]

    def setx2(self, val):
        self._p2[0] = val
    x2 = property(getx2, setx2)
    
    def gety2(self):
        return self._p2[1]

    def sety2(self, val):
        self._p2[1] = val
    y2 = property(gety2, sety2)


class RectGeometry(object):
    
    def __init__(self, x, y, width, height, position=None):
        super(RectGeometry, self).__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self._position = Vec2d(0.0, 0.0)
        if position is None:
            self.position = self.rect.center
        else:
            self.position = position

    ## entity's collided, static method used by QuadTree callback
    collided = staticmethod(rect_collided_other)
    
    def getpoints(self):
        r = self.rect
        return r.topleft, r.topright, r.bottomright, r.bottomleft
    points = property(getpoints)
    
    def getposition(self):
        """GOTCHA: Something like "rect_geom.position.x += 1" will not do what
        you expect. That operation does not update the rect instance variable.
        Instead use "rect_geom.position += (1,0)".
        """
        return self._position

    def setposition(self, val):
        p = self._position
        p.x, p.y = val
        self.rect.center = round(p.x), round(p.y)
    position = property(getposition, setposition)


class CircleGeometry(object):
    
    def __init__(self, origin, radius):
        super(CircleGeometry, self).__init__()
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self._position = Vec2d(0.0, 0.0)
        self.position = origin

    ## entity's collided, static method used by QuadTree callback
    collided = staticmethod(circle_collided_other)
    
    def getorigin(self):
        return Vec2d(self._position)
    origin = property(getorigin)
    
    def getradius(self):
        return self.rect.width // 2

    def setradius(self, val):
        self.rect.size = Vec2d(val, val) * 2
        self.position = self.position
    radius = property(getradius, setradius)
    
    def getposition(self):
        """GOTCHA: Something like "circle_geom.position.x += 1" will not do what
        you expect. That operation does not update the rect instance variable.
        Instead use "circle_geom.position += (1,0)".
        """
        return self._position

    def setposition(self, val):
        p = self._position
        p.x, p.y = val
        self.rect.center = round(p.x), round(p.y)
    position = property(getposition, setposition)


class PolyGeometry(object):
    
    def __init__(self, points, position=None):
        super(PolyGeometry, self).__init__()
        self._points = points
        
        minx = reduce(min, [x for x, y in points])
        width = minx + reduce(max, [x for x, y in points]) + 1
        miny = reduce(min, [y for x, y in points])
        height = miny + reduce(max, [y for x, y in points]) + 1
        self.rect = pygame.Rect(minx, miny, width, height)
        
        self._position = Vec2d(0.0, 0.0)
        if position is None:
            self.position = self.rect.center
        else:
            self.position = position

    ## entity's collided, static method used by QuadTree callback
    collided = staticmethod(poly_collided_other)
    
    def getpoints(self):
        left, top = self.rect.topleft
        return [(left + x, top + y) for x, y in self._points]
    points = property(getpoints)
    
    def getposition(self):
        """GOTCHA: Something like "poly_geom.position.x += 1" will not do what
        you expect. That operation does not update the rect instance variable.
        Instead use "poly_geom.position += (1,0)".
        """
        return self._position

    def setposition(self, val):
        p = self._position
        p.x, p.y = val
        self.rect.center = round(p.x), round(p.y)
    position = property(getposition, setposition)


def circle_intersects_circle(origin1, radius1, origin2, radius2):
    """Circle vs circle collision test.
    
    Return True if circles intersect, else return False.
    """
    x = origin1[0] - origin2[0]
    y = origin1[1] - origin2[1]
    dist = sqrt(x * x + y * y)
    return dist <= radius1 + radius2


def circle_intersects_line(origin, radius, line_segment):
    """Circle vs line collision test. Return point of contact, or None.
    
    Return True if line_segment intersects the circle defined by origin and
    radius. Return False if they do not intersect.
    """
    A, B = Vec2d(line_segment[0]), Vec2d(line_segment[1])
    C = Vec2d(origin)
    AC = C - A
    AB = B - A
    ab2 = AB.dot(AB)
    acab = AC.dot(AB)
    t = acab / ab2
    
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    
    P = AB * t + A
    
    H = P - C
    h2 = H.dot(H)
    r2 = radius * radius
    
#    return h2 <= r2
    if h2 <= r2:
        return P
    else:
        return None


def circle_intersects_rect(origin, radius, rect):
    """Circle vs rect collision test.
    
    Return True if the shapes intersect, else return False. rect must be a
    pygame.Rect().
    """
    for line in rect_to_lines(rect):
        if circle_intersects_line(origin, radius, line):
            return True
    return False


def circle_intersects_poly(origin, radius, points):
    """Circle vs polygon collision test.
    
    Points must describe a "closed" polygon with no redundant points. Winding is
    a factor.
    """
    for line in points_to_lines(points):
        if circle_intersects_line(origin, radius, line):
            return True
    return False


def line_intersects_line(line_1, line_2):
    """Line vs line collision test.
    
    Returns [x,y] if the lines intersect, otherwise []. [x,y] is the point
    of intersection.
    
    The return values are suitable for "if collided: ... else: ..." usage.
    Accessing the (x,y) values is optional.
    """
    a, b = (x1, y1), (x2, y2) = line_1
    c, d = (x3, y3), (x4, y4) = line_2
    
    # Fail if either line segment is zero-length.
    if a == b or c == d:
        return []

    sx1 = float(x2 - x1)
    sy1 = float(y2 - y1)
    sx2 = float(x4 - x3)
    sy2 = float(y4 - y3)

    # Fail if lines coincide (end points are along the same line).
    s1 = (-sx2 * sy1 + sx1 * sy2)
    t1 = (-sx2 * sy1 + sx1 * sy2)
    if s1 == 0 or t1 == 0:
        return []

    s = (-sy1 * (x1 - x3) + sx1 * (y1 - y3)) / s1
    t = (sx2 * (y1 - y3) - sy2 * (x1 - x3)) / t1

    # if s >= 0 and s <= 1 and t >= 0 and t <= 1:
    if 0 <= s <= 1 and 0 <= t <= 1:
        # Collision detected
        i_x = x1 + (t * sx1)
        i_y = y1 + (t * sy1)
        return [(i_x, i_y)]

    # No collision
    return []


def lines_intersect_lines(lines1, lines2, fast=True):
    """Line lists intersection test.
    
    Tests one list of lines against another. Returns a list of intersecting
    (x,y) pairs, or an emtpy list if there are no collisions.
    
    This does not detect containment. point_in_poly() can be used to test for
    containment.
    """
    crosses = []
    for line1 in lines1:
        for line2 in lines2:
            cross = line_intersects_line(line1, line2)
            if cross:
                crosses.append(cross[0])
                if fast:
                    return crosses
    return crosses


def line_intersects_rect(line, rect, fast=True):
    """Line vs rect intersection test.
    
    rect must be a pygame.Rect().
    
    Tests a line against the edges of a rect. Returns a list of intersecting
    (x,y) pairs, or an emtpy list if there are no collisions.
    
    This does not detect containment. point_in_poly() can be used to test for
    containment.
    """
    rect_lines = rect_to_lines(rect)
    return lines_intersect_lines([line], rect_lines, fast)


def line_intersects_poly(line, points, fast=True):
    """Line vs poly test.
    
    Tests a line against a polygon. Returns a list of intersecting
    (x,y) pairs, or an emtpy list if there are no collisions.
    
    This does not detect containment. point_in_poly() can be used to test for
    containment.
    """
    poly_lines = points_to_lines(points)
    return lines_intersect_lines([line], poly_lines, fast)


def poly_intersects_rect(points, rect, fast=True):
    """Poly vs rect intersection test.
    
    Tests a polygon against a rect. rect must be a pygame.Rect(). Returns a
    list of intersecting (x,y) pairs, or an emtpy list if there are no
    collisions.
    
    This does not detect containment. point_in_poly() can be used to test for
    containment.
    """
    poly_lines = points_to_lines(points)
    rect_lines = rect_to_lines(rect)
    return lines_intersect_lines(poly_lines, rect_lines, fast)


def poly_intersects_poly(points1, points2, fast=True):
    """Poly vs poly intersection test.
    
    Tests a polygon against another polygon. Returns a list of intersecting
    (x,y) pairs, or an emtpy list if there are no collisions.
    
    This does not detect containment. point_in_poly() can be used to test for
    containment.
    """
    lines1 = points_to_lines(points1)
    lines2 = points_to_lines(points2)
    return lines_intersect_lines(lines1, lines2, fast)


def points_to_lines(points):
    """Return a list of end-point pairs assembled from a "closed" polygon's
    points.
    """
    lines = []
    ix = [i for i in range(len(points))]
    ix.append(0)
    for i in range(0, len(points)):
        line = points[ix[i]], points[ix[i + 1]]
        lines.append(line)
    return lines


def rect_to_lines(rect):
    """Return a list of end-point pairs assembled from a pygame.Rect's corners.
    """
    tl, tr, br, bl = rect.topleft, rect.topright, rect.bottomright, rect.bottomleft
    return [(tl, tr), (tr, br), (br, bl), (bl, tl)]


if __name__ == '__main__':
    def sequal(a, b):
        if len(a) != len(b):
            return False
        for i, n in enumerate(a):
            if n != b[i]:
                return False
        return True
    line = LineGeometry(10, 10, 50, 50)
    assert line.points == ((10, 10), (50, 50))
    line.p1 = 20, 20
    assert line.points == ((20, 20), (50, 50))
    line.p2 = 60, 60
    assert line.points == ((20, 20), (60, 60))
    line.points = 10, 20, 30, 40
    assert line.points == ((10, 20), (30, 40))
    line.points = (20, 20), (30, 40)
    assert line.points == ((20, 20), (30, 40))
    try:
        line.points = 1, 2, 3, 4, 5
    except ValueError:
        print('LineGeometry: all tests passed')
