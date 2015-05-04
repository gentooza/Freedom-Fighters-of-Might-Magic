Freedom Fighters of Might & Magic
========

Freedom Fighters of Might & Magic is a strategy/rpg game based on the Heroes of Might & Magic saga. FFMM will be different with its own rules and it won't be a pure clone version.

For now it's in alpha version, is not playable.

me (gentooza), I've just begun using python at work, and seeing how easy is to use it I've started to build a game (the dream of any boring industrial programmer) :-)

everybody is invited to participate and learn!

see ROADMAP for future works needed
,see CHANGELOG to see works already done

##Dependencies

I'm using python 3.4 and pygame 1.92 (python 3.4 is the default in my Trisquel 7 GNU/Linux)

I've based the work in the libraries:

* [pygbutton](https://github.com/asweigart/pygbutton) for creating buttons
* [pyganim](https://github.com/asweigart/pyganim) for sprites animation
* [gummworld2](https://bitbucket.org/gummbum/gummworld2/wiki/Home) for a basic game engine, minimap, etc.

###for installing pygame 1.92 for pyhton3 you have to do this:

####under ubuntu 14.04/trisquel7:

* install dependencies
```
sudo apt-get install mercurial python3-dev python3-numpy libav-tools \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
``` 
* Grab source
```
hg clone https://bitbucket.org/pygame/pygame
``` 
* Finally build and install
```
cd pygame
python3 setup.py build
sudo python3 setup.py install
```
source:[pygame.org](http://www.pygame.org/wiki/CompileUbuntu)

##Execute

####under ubuntu 14.0.4/Trisquel7:
```
python3 main.py
```

##images license

All the artwork is the battle for wesnoth artwork, not from FFMM, so it's licensed under the license estipulated by the wesnoth team

[web page of "battle for wesnoth"](http://www.wesnoth.org/)


##license

Freedom Fighters of Might & Magic is licensed under the GNU GPL3

##contributors

* gentooza : joa.cuellar(at)mail.riseup.net