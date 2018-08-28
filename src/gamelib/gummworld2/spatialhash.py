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

__all__ = ['SpatialHash']


from collections import defaultdict
from itertools import chain

from pygame import Rect

try:
    from gummworld2 import geometry
    from gummworld2.geometry import COLLISION_FUNCS
except:
    import geometry
    from geometry import COLLISION_FUNCS


class SpatialHash(object):
    def __init__(self, cell_size=50):
        # Only sort_key is writeable!
        self.sort_key = None

        # Everything else is readonly!

        self.cell_size = int(cell_size)
        self.coll_tests = 0

        # buckets = {(x, y): set(entity, ...)}
        # cell_ids = {entity: [(x, y), ...]}
        self.buckets = defaultdict(set)
        self.cell_ids = defaultdict(set)

        # used to assist rect-from-line calculations
        self._temp_rect = Rect(0, 0, 1, 1)

        # caching sorted entities
        self.dirty = False
        self.sorted_entities = []

        # caching cell ranges
        self._cell_ranges_cache = {}

    @property
    def entities(self):
        """Return the entire list of entities.
        
        This method honors self.sort_key.
        """
        if self.sort_key:
            if self.dirty:
                self.sorted_entities[:] = sorted(self.cell_ids, key=self.sort_key)
                self.dirty = False
            return self.sorted_entities[:]
        else:
            return self.cell_ids.keys()
    
    def add(self, entity):
        """Add or re-add obj. Return True if in bounds, else return False.
        
        If this method returns False then the object is completely out of
        bounds and cannot be stored in this space.
        
        Note that when obj changes its position, you must add it again so that
        its cell membership is updated. This method first removes the object if
        it is already in the spatial hash.
        """
        self.addlist((entity, ))

    def addlist(self, entities):
        self.dirty = True
        self__cells = self.buckets
        self__cell_size = self.cell_size
        self__entity_to_cells = self.cell_ids
        self__remove = self.remove
        self__cell_ranges_cache = self._cell_ranges_cache
        for e in entities:
            if e in self__entity_to_cells:
                self__remove(e)

            rect = e.rect
            x = rect[0]
            y = rect[1]
            left = x // self__cell_size
            right = (x + rect[2]) // self__cell_size
            top = y // self__cell_size
            bottom = (y + rect[3]) // self__cell_size

            # cache generated range
            cell_key = left, top, right, bottom
            try:
                cell_range = self__cell_ranges_cache[cell_key]
            except:
                cell_range = [(x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)]
                self__cell_ranges_cache[cell_key] = cell_range

            self__entity_to_cells_e__add = self__entity_to_cells[e].add
            for _cell_id in cell_range:
                self__cells[_cell_id].add(e)
                self__entity_to_cells_e__add(_cell_id)

    def remove(self, entity):
        self__buckets = self.buckets
        self__entity_to_cells = self.cell_ids
        self__entity_to_cells__pop = self__entity_to_cells.pop
        if entity in self.cell_ids:
            for cell_id in self__entity_to_cells__pop(entity):
                self__buckets[cell_id].remove(entity)
                # remove empty bucket
                # if not self__buckets[cell_id]:
                #     self__buckets.pop(cell_id)

    def removelist(self, entities):
        self__buckets = self.buckets
        self__entity_to_cells = self.cell_ids
        self__entity_to_cells__pop = self__entity_to_cells.pop
        for e in entities:
            if e in self__entity_to_cells:
                for cell_id in self__entity_to_cells__pop(e):
                    self__buckets[cell_id].remove(e)
                    # remove empty bucket
                    # if not self__buckets[cell_id]:
                    #     self__buckets.pop(cell_id)

    def get_nearby_entities(self, entity):
        """Return a list of entities that share the same cells as entity.
        
        This method honors self.sort_key.
        """
        nearby_ents = []
        extend = nearby_ents.extend
        buckets = self.buckets
        cell_ids = self.intersect_cell_ids(entity.rect)
        for cell_id in cell_ids:
            if cell_id in buckets:
                extend(buckets[cell_id])
        if self.sort_key:
            nearby_ents.sort(key=self.sort_key)
        return nearby_ents
    
    def get_cell_id(self, x, y):
        """Return the cell_id of the cell that contains point (x,y).
        """
        cell_size = self.cell_size
        idx = x // cell_size, y // cell_size
        return idx
    
    def intersect_cell_ids(self, rect):
        """Return list of cell ids that intersect rect.
        
        The return value is a list of int. Each int is a key for self.buckets. Note: the values are NOT checked for
        presence in buckets; so if self.buckets[i] is accessed directly, empty buckets may be accidentally created.
        
        :param rect: pygame.Rect; bounding rect
        :return: list of int
        """
        # Not pretty, but these ugly optimizations shave 50% off run-time
        # versus function calls and attributes. This method is called a lot.
        
        cell_size = self.cell_size
        cell_ranges_cache = self._cell_ranges_cache

        x = rect[0]
        y = rect[1]
        left = x // cell_size
        right = (x + rect[2]) // cell_size
        top = y // cell_size
        bottom = (y + rect[3]) // cell_size

        # cache generated range
        cell_key = left, top, right, bottom
        try:
            cell_range = cell_ranges_cache[cell_key]
        except:
            cell_range = [(x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)]
            cell_ranges_cache[cell_key] = cell_range

        return cell_range

    def intersect_entities(self, rect):
        """Return list of entities whose rects intersect rect.
        
        This method honors self.sort_key.
        """
        result = {}
        colliderect = rect.colliderect
        rg = geometry.RectGeometry(*rect)
        buckets = self.buckets

        for cell_id in self.intersect_cell_ids(rect):
            if cell_id not in buckets:
                continue
            for o in buckets[cell_id]:
                try:
                    if colliderect(o.rect):
                        try:
                            if o.collided(o, rg, True):
                                result[o] = 1
                        except:
                            result[o] = 1
                except:
                    try:
                        if o.collided(o, rg, True):
                            result[o] = 1
                    except:
                        pass
        result = list(result)
        if self.sort_key:
            result.sort(key=self.sort_key)
        return result
    
    def get_cell_pos(self, cell_id):
        """Return the world coordinates for topleft corner of cell.
        """
        x, y = cell_id
        cell_size = self.cell_size
        return x * cell_size, y * cell_size
    
    def collideany(self, entity, do_fine=True):
        """Return True if entity collides with any other object, else False.
        """
        colliderect = Rect.colliderect
        entity__type = None

        r = entity.rect

        if do_fine:
            try:
                entity__type = entity.collision_type
            except:
                entity__type = None

        others = self.get_nearby_entities(entity)

        if do_fine and entity__type is not None:
            for o in others:
                if colliderect(r, o.rect) and \
                        COLLISION_FUNCS[entity__type, o.collision_type](entity, o, True):
                    return True
        else:
            for o in others:
                if colliderect(r, o.rect):
                    return True

        return False
    
    def collide(self, entity, do_fine=True):
        """Return list of entities that collide with entity.
        """
        result = []
        result_append = result.append
        colliderect = Rect.colliderect
        entity__type = None

        r = entity.rect

        if do_fine:
            try:
                entity__type = entity.collision_type
            except:
                entity__type = None

        others = self.get_nearby_entities(entity)

        if do_fine and entity__type is not None:
            for o in others:
                colliderect(r, o.rect) and \
                    COLLISION_FUNCS[entity__type, o.collision_type](entity, o, True) and \
                    result_append(o)
        else:
            for o in others:
                colliderect(r, o.rect) and result_append(o)

        self.coll_tests = len(others)
        return result

    def collidedict(self, entities, do_fine=True):
        """Return dict of entities that collide with entities.

        The entities in the SpatialHash will be checked against the entities argument. The nested structure of the
        returned dict is: {entity: set(entity, ...)}.

        The default behavior is to try rect and then fine collision tests. The algorithm detects the presence or the
        rect and/or collided attributes, and automatically uses whatever is present. If collided is not present, then
        the result of the rect test will be kept. If rect is not present, then collided is assumed to be present. If
        both are present, then rect provides a course test and collided is checked only if the rects collide.

        Set do_fine equal to False to unconditionally bypass the collided check and save a little CPU (see
        geometry.*_collided for more info on fine geometric collision checking).

        :param entities: sequence; entities to be checked against the SpatialHash's contents
        :param do_fine: bool; if True then try fine collisions, else if False then skip them
        :return: {entity: set(entity, ...)}
        """
        result = {}
        buckets = self.buckets
        cell_size = self.cell_size
        cell_ranges_cache = self._cell_ranges_cache
        chain_from_iterable = chain.from_iterable
        colls = set()
        colls_add = set.add
        colls_discard = set.discard
        colliderect = Rect.colliderect
        e__type = None
        tests = 0

        for e in entities:
            r = e.rect

            # calculate call range
            x = r[0]
            y = r[1]
            left = x // cell_size
            top = y // cell_size
            right = (x + r[2]) // cell_size
            bottom = (y + r[3]) // cell_size

            # cache generated range
            cell_key = left, top, right, bottom
            try:
                cell_range = cell_ranges_cache[cell_key]
            except:
                cell_range = [(x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)]
                cell_ranges_cache[cell_key] = cell_range

            others = chain_from_iterable(buckets[i] for i in cell_range if i in buckets)

            if do_fine:
                try:
                    e__type = e.collision_type
                except:
                    e__type = None

            if do_fine and e__type is not None:
                for o in others:
                    colliderect(r, o.rect) and \
                        COLLISION_FUNCS[e__type, o.collision_type](e, o, True) and \
                        colls_add(colls, o)
            else:
                for o in others:
                    colliderect(r, o.rect) and colls_add(colls, o)

            # update results
            if colls:
                colls_discard(colls, e)
                if colls:
                    result[e] = colls
                    colls = set()

        self.coll_tests = tests
        return result

    def collidealldict(self, rect=None, do_fine=True, fat=False):
        """Return dict of all collisions.

        The entities in the SpatialHash are checked among themselves. The nested structure of the returned dict is:
        {entity: set(entity, ...)}.

        If rect is specified, only the cells that intersect rect will be checked.

        The default behavior is to try rect and then fine collision tests. The algorithm detects the presence or the
        rect and/or collided attributes, and automatically uses whatever is present. If collided is not present, then
        the result of the rect test will be kept. If rect is not present, then collided is assumed to be present. If
        both are present, then rect provides a course test and collided is checked only if the rects collide.

        Set do_fine equal to False to unconditionally bypass the collided check and save a little CPU (see
        geometry.*_collided for more info on fine geometric collision checking).

        If fat is True, then the returned dict will have a key for every entity and the value will be the key's
        colliding entities. This is ideal for checking collisions in bulk, and then obtaining the collisions by key: but
        the data set will contain collisions forwards and backwards, which is expensive to build and walk. If fat is
        False, then sparse results are returned. This is ideal for walking the dict to pair the collisions, as each
        collision only exists once in the data set: but entities cannot simply be looked up by key.

        :param rect: pygame.Rect; optional rect to cull the space to check
        :param do_fine: bool; if True then try fine collisions, else if False then skip them
        :param fat: bool/ if True then return full dict with redundant collisions; else return a sparse dict
        :return: {entity: set(entity, ...)}
        """
        result = defaultdict(set)
        colliderect = Rect.colliderect
        e__type = None
        tests = 0

        if rect:
            buckets = self.buckets
            cells = [buckets[i] for i in self.intersect_cell_ids(rect)]
        else:
            cells = self.buckets.values()

        for cell in cells:
            cell = list(cell)
            for i, e in enumerate(cell):
                e__rect = e.rect

                if do_fine:
                    try:
                        e__type = e.collision_type
                    except:
                        e__type = None

                colls_e = []
                colls_e__append = colls_e.append
                offset = 0 if fat else i + 1
                for o in cell[offset:]:
                    if o is e:
                        continue
                    tests += 1
                    if do_fine and e__type is not None:
                        if colliderect(e__rect, o.rect):
                            if COLLISION_FUNCS[e__type, o.collision_type](e, o, True):
                                colls_e__append(o)
                    else:
                        colliderect(e__rect, o.rect) and colls_e__append(o)
                if colls_e:
                    result[e].update(colls_e)
                try:
                    if e in result:
                        result[e].remove(e)
                        if not result[e]:
                            result.pop(e)
                except:
                    pass

        self.coll_tests = tests
        return result

    def clear(self):
        """Clear all objects.
        """
        self.dirty = True
        self.buckets.clear()
        self.cell_ids.clear()
        self.sorted_entities = []

    def gen_cell_ranges_cache(self, rect, cell_span=(3, 3)):
        """pre-generate ranges on the first two orders (1x1, 1x2, 2x2)

        :param rect: (x, y, w, h): the bounding rect, typically the world rect
        :param cell_span: tuple; (w, h) number of cells to span
        :return: None
        """
        cell_size = self.cell_size
        x, y, w, h = rect
        left = x // cell_size
        top = y // cell_size
        right = (x + w) // cell_size
        bottom = (y + h) // cell_size

        cell_ranges_cache = self._cell_ranges_cache
        y_range = range(top, bottom)
        for x in range(left, right):
            for y in y_range:
                for right in range(x, x + cell_span[0]):
                    for bottom in range(y, y + cell_span[1]):
                        cell_key = x, y, right, bottom
                        if cell_key not in cell_ranges_cache:
                            yr = range(y, bottom + 1)
                            xr = range(x, right + 1)
                            cell_range = [(_x, _y) for _y in yr for _x in xr]
                            cell_ranges_cache[cell_key] = cell_range

    # def _get_rect_for_line(self, obj):
    #     """Lines don't have a rect attribute. Use self._temp_rect to fudge it.
    #     """
    #     points = obj.points
    #     rect = self._temp_rect
    #     x1, y1 = points[0]
    #     x2, y2 = points[1]
    #     if x1 > x2:
    #         t = x1
    #         x1 = x2
    #         x2 = t
    #     if y1 > y2:
    #         t = y1
    #         y1 = y2
    #         y2 = t
    #     rect.topleft = x1, y1
    #     rect.width = x2 - x1
    #     rect.height = y2 - y1
    #     return rect
    
    def __iter__(self):
        """This method honors self.sort_key."""
        if self.sort_key:
            if self.dirty:
                self.sorted_entities[:] = sorted(self.cell_ids, key=self.sort_key)
                self.dirty = False
            for obj in self.sorted_entities:
                yield obj
        else:
            for obj in self.cell_ids:
                yield obj
    
    def __contains__(self, obj):
        return obj in self.cell_ids
    
    def __len__(self):
        return len(self.cell_ids)
    
    def __str__(self):
        return '<{}({}) at {}>'.format(self.__class__.__name__, str(self.cell_size), id(self))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.cell_size))
