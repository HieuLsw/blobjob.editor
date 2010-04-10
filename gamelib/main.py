"""
    BlobJob Map Editor
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import data
import cocos
from cocos import tiles
import pyglet
from cocos.director import director
from cocos.actions.interval_actions import ScaleTo


class MapEditorControlLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        super(MapEditorControlLayer,self).__init__()
        self.kb = pyglet.window.key.KeyStateHandler()
        self.kbhandler = director.window.push_handlers(self.kb)
        self.scale_speed = 5
        self.max_scale = 1
        self.min_scale = 0.1
        self.hover_tile = None
        
    def on_exit(self):
        director.window.remove_handlers(self.kb)
        
    def on_mouse_scroll(self,x,y,scroll_x,scroll_y):
        print x,y,scroll_x,scroll_y
        manager = self.parent.manager
        new_scale = max(self.min_scale, manager.scale + (self.scale_speed * scroll_y)/10.0)
        new_scale = min(self.max_scale, new_scale )
        print "scaling from %s to %s (%s)"%(manager.scale,new_scale,((self.scale_speed * scroll_y)/10.0))
        print ((self.scale_speed * scroll_y)/10.0)
        manager.do(ScaleTo(new_scale,duration=0.5))
        manager.y = 0
        
        manager.force_focus(manager.fx,manager.fy)

    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        manager = self.parent.manager
        manager.force_focus(manager.fx - dx/manager.scale, manager.fy-dy/manager.scale)

    def on_mouse_motion(self,x,y,dx,dy):
        manager = self.parent.manager
        level = self.parent.level
        (wSizeX,wSizeY) = director.get_window_size()

        (sx,sy) = director.get_virtual_coordinates(x,y)
        sx = sx/manager.scale
        sy = sy/manager.scale
        sx += manager.fx - wSizeX/2
        sy += manager.fy - wSizeY/2
        for id,layer in level.find(cocos.tiles.MapLayer):
            if(self.hover_tile):
                tile = self.hover_tile
                layer.set_cell_opacity(tile.i, tile.j, 255)
            cell = layer.get_at_pixel(sx,sy)
            if(cell):
                tile = cell
                if(tile):
                    self.hover_tile = tile
                    layer.set_cell_opacity(tile.i, tile.j, 200)
#                    print(self.hover_tile)
                    self.hover_tile.image = 0.5
        return type

class MapEditorScene(cocos.scene.Scene):
    def __init__(self):
        super(MapEditorScene,self).__init__()
        self.add(MapEditorControlLayer())
        self.map_layer = cocos.layer.Layer()
        self.manager = None
        self.load_xml('data/maps/level1.xml')
        
    def load_xml(self, level_xml):
        try:
            self.map_layer.walk(self.map_layer.remove)
            self.remove(self.manager)
        except:
            pass

        self.manager = cocos.layer.ScrollingManager()
        self.add(self.manager)
        level = tiles.load(level_xml)
        mz = 0
        mx = 0
        my = 0
        for id, layer in level.find(tiles.MapLayer):
            self.manager.add(layer, z=layer.origin_z)
            mz = max(layer.origin_z, mz)
            mx = max(layer.px_width, mx)
            my = max(layer.px_height, my)

        self.level = level
        self.mx = mx
        self.my = my
        self.mz = mz

def main():
    pyglet.font.add_directory(data.filepath('fonts'))
    pyglet.resource.path.append(data.filepath('.'))
    pyglet.resource.path.append(data.filepath('maps'))
    pyglet.resource.path.append(data.filepath('chars'))
    pyglet.resource.reindex()

    director.init(resizable=True, width=800, height=600, audio=None)
    s = MapEditorScene()
    
    director.run( s )
