WHAT'S IN THE DISTRIBUTION
==========================

data/
  The game resource directory. The data module knows how to look files up in
  here.

docs/
  * Gummworld2 HTML docs produced by pydoc.
  * A third_party/ subdirectory containing licenses and other readmes for
    third-party components included with Gummworld2.

examples/
  Demonstrations of some of what's possible with Gummworld2:
  * Scrolling maps
  * Supermaps: autoloading and unloading maps too big to fit in memory
  * Tiled maps
  * Custom maps: world editor included--req. Python 2.6 or 2.7
  * Parallax layers
  * Collapsing and reducing map layers to boost performance
  * SpatialHash exercisers
  * Geometry collisions: any line or polygon versus any other
  * Views (subsurfaces)
  * HUDs
  * Renderer: newest feature; super fast, multilayer, high tile count

gamelib/
  Subdirectories:
  * gummworld2/, the map scrolling library for use in games
  * pgu/gui/, a widget based GUI included for the world editor; you're free to
    use it, but it's not required for games
  * tiledtmxloader/, an orthogonal Tiled map loader

make_docs, pydoc
  The script used to create the HTML docs, and to start the pydoc viewer web
  service.

paths.py*
  Convenient module for run-time configuration of library path.

world_editor.py*
  The world editor. Make rects, circles, polygons overlaying a map; save 'em,
  load 'em in a game, use 'em as collidable objects.


USING GUMMWORLD2
================

See the docs/ directory of the distribution for the HTML version of library
docstrings. There is a convenience pydoc script in the base directory that can
be used to start a PyDoc server.

There are many simple examples in the examples/ directory.

See gamelib/gummworl2/toolkit.py for examples of how to work directly with
classes like BasicMap, BasicLayer, Camera, HUD, etc.

If that's not enough to get you rolling, drop by the discussion group to get
some personal help: https://groups.google.com/group/gummworld2


REQUESTING HELP AND IMPROVEMENTS
================================

Start a discussion at https://groups.google.com/group/gummworld2. That way
others may benefit from the exchange.

Enhancement requests and bug reports may be submitted at the project site
https://bitbucket.org/gummbum/gummworld2.
