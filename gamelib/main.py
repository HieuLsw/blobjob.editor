'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from cocos.director import director

from game_editor_scene import GameEditorScene

def main():
    print sys.argv

    pyglet.font.add_directory(data.filepath('fonts'))
    pyglet.resource.path.append(data.filepath('.'))
    pyglet.resource.reindex()

    director.init(resizable=True, width=800, height=600, audio=None)
    director.window.("BlobEdit")
    s = GameEditorScene()
    director.run( s )
    
#    print data.load('sample.txt').read()
