#! /usr/bin/env python

#
#  Freedom Fighters of Might & Magic
#
#  Copyright 2014-2015 by it's authors. 
#
#  Some rights reserved. See COPYING, AUTHORS.
#  This file may be used under the terms of the GNU General Public
#  License version 3.0 as published by the Free Software Foundation
#  and appearing in the file COPYING included in the packaging of
#  this file.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#



try:
   import sys
   from src import paths
   import start
except ImportError as err:
   print("couldn't load module. %s" % (err))
   sys.exit(2)




#INTILIALIZATION
#old 1014,965
resolution = (1024,768)
version = '0.0.6 ALPHA'
strCaption = 'FFMM ' + version
tile_size=(30, 30) 
map_size=(100, 100)
minimap_pos = (600,100)
minimap_size = (120,120)
FPS = 50
NULL = 'NULL'

parameters = {'resolution' : resolution,'strcaption' : strCaption,'caption' : NULL,'tile_size' : tile_size,'map_size' : map_size, 'minimap_pos' : minimap_pos, 'minimap_size' : minimap_size, 'FPS' : FPS, 'version' : version , 'fullscreen' : False }


FFMM = start.app(parameters)
#DISPLAY
FFMM.setDisplay()

#GAME RUN!!
FFMM.run()

	





