"""
    BlobJob Map Editor
"""
import pyglet.window

from cocos.actions.base_actions import IntervalAction
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import data
import cocos
from cocos import tiles
import pyglet
from cocos.director import director
import dialogs
import blobedit_dialogs

class SetScaleTo(IntervalAction):
    def init(self,scale,duration=0.5):
        self.duration = duration
        self.dest_scale = scale
        print "Scale to %s"%scale
    def start(self):
        super(SetScaleTo,self).start()
        self.origin_scale = self.target.scale
        self.delta_scale = self.dest_scale - self.origin_scale
        self.scale_per_t = self.delta_scale / self.duration
        print "interval scaling from %f to %f"%(self.origin_scale, self.dest_scale)
    def update(self, t):
        new_scale = self.origin_scale + self.delta_scale * t
        self.target.set_scale(new_scale)

class MapEditorControlLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        self.prevent_exit_on_escape_key = False
        super(MapEditorControlLayer,self).__init__()
        self.kb = pyglet.window.key.KeyStateHandler()
        self.kbhandler = director.window.push_handlers(self.kb)
        self.scale_speed = 2.0
        self.max_scale = 1.0
        self.min_scale = 0.1
        self.hover_tile = None
        self.current_cell = None
        
    def on_exit(self):
        director.window.remove_handlers(self.kb)
        
    def on_resize(self,w,h):
        manager = self.parent.manager
        manager.set_focus(manager.fx,manager.fy)
#        manager.view_w = w/2
#        (manager.origin_x,manager.origin_y) = director.get_real_coordinates(x,y)

    def on_mouse_scroll(self,x,y,scroll_x,scroll_y):
        if(self.parent.level is not None):
            print x,y,scroll_x,scroll_y
            manager = self.parent.manager
            new_scale = max(self.min_scale, manager.scale + (self.scale_speed * scroll_y)/10.0)
            new_scale = min(self.max_scale, new_scale )
            duration = 0.5

            print "scaling from %s to %s (%s)"%(manager.scale,new_scale,duration)
    #        manager.do(ScaleTo(new_scale,duration=0.5))
            manager.do(SetScaleTo(scale=new_scale,duration=duration))
    #        manager.set_scale(new_scale)
            manager.y = 0

            manager.force_focus(manager.fx,manager.fy)

    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        if(self.parent.level is not None):
            if(self.parent.active_tool == 'move'):
                manager = self.parent.manager
                manager.set_focus(manager.fx - dx/manager.scale, manager.fy-dy/manager.scale)
            if(self.parent.active_tool == 'pencil'):
                self.replace_with_current(x, y)

    def on_mouse_motion(self,x,y,dx,dy):
        manager = self.parent.manager
        level = self.parent.level
        layer = self.parent.active_layer
        director.window.set_mouse_cursor(self.parent.active_mouse_cursor)
        if(level is not None):
            if(self.parent.active_tool in ['pencil','eraser']):

        #        (sx,sy) = director.get_virtual_coordinates(x,y)
                (sx,sy) = self.screen_to_map(x,y)
                
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
    def screen_to_map(self, x,y):
        manager = self.parent.manager
        (wSizeX,wSizeY) = (director.window.width,director.window.height)
        sx = x/manager.scale
        sy = y/manager.scale
        sx += manager.fx - wSizeX/2
        sy += manager.fy - wSizeY/2
        return (sx,sy)
    
    def on_mouse_press(self,x,y,buttons,modifiers):
        print "click on %s,%s, selected tile: %s"%(x,y,self.parent.active_tile)
        if(self.parent.active_tool == 'pencil'):
            self.replace_with_current(x,y)

    def replace_with_current(self,x,y):
        tileset = self.parent.tilesets[0]
        layer = self.parent.active_layer
        if (layer is not None):
            cx,cy = self.screen_to_map(x, y)
            current_cell = layer.get_at_pixel(cx,cy)
            if(self.current_cell is None or self.current_cell != current_cell):

                self.current_cell = current_cell
                new_tile = tileset.get(self.parent.active_tile)
                current_cell.tile = new_tile
                layer.set_dirty()
        
    
        
                
    def on_key_press(self,key,modifiers):
        if(key == pyglet.window.key.ESCAPE):
            return self.prevent_exit_on_escape_key

class MapEditorScene(cocos.scene.Scene):
    def __init__(self):
        super(MapEditorScene,self).__init__()
        self.last_path = data.filepath('maps')
        self.load_mouse_cursors()
        self.add(MapEditorControlLayer())
        self.map_layer = cocos.layer.Layer()
        self.active_tool = None
        self.active_tile = None
        self.level = None
        self.active_layer = None
        self.dialog_layer = dialogs.DialogLayer()
        self.manager = cocos.layer.ScrollingManager()
        self.add(self.manager)
        self.add(self.dialog_layer)
        self.statusbar = blobedit_dialogs.StatusBarDialog()
        self.toolbar = blobedit_dialogs.ToolBarDialog(
            on_tool_select=self.on_tool_select,
            on_button_click=self.on_button_click
            )
        self.tilebar = None
        self.dialog_layer.add_dialog(self.toolbar)
        self.dialog_layer.add_dialog(self.statusbar)
        self.on_tool_select(self.toolbar.active_tool)
        self.load_xml('data/maps/level1.xml')


    def on_button_click(self,id):
        print "callback for button <%s>"%id
        if id == "Open":
            print "show open file dialog"
            self.dialog_layer.add_dialog(
                blobedit_dialogs.OpenFileDialog(
                    self.last_path,
                    on_open = self.on_file_open_clicked
                    )
                )
        elif id == "Save":
            self.save_map()
            self.dialog_layer.add_dialog(
                blobedit_dialogs.PopupMessage(
                    "File Saved"
                    )
                )
        elif id == "Quit":
            director.pop()
        else:
            self.dialog_layer.add_dialog(blobedit_dialogs.PopupMessage("Not implemented: <%s>"%id))

    def on_file_open_clicked(self, file):
        print file
        self.last_path = os.path.dirname(file)
        self.load_xml(file)
        
    def on_tool_select(self,id):
        if(hasattr(self, 'toolbar')):
            self.statusbar.set_text(self.toolbar.get_help_text(id))
        else:
            self.statusbar.set_text(id)
        self.active_tool = id
        self.update_mouse_cursor()

    def load_mouse_cursors(self):
        self.mouse_cursors = {
            'default': None,
            'move': pyglet.window.ImageMouseCursor(
                pyglet.image.load(
                    os.path.join(data.filepath('theme'),'icons',
                    'transform-move.png')),
                    hot_x = 11, hot_y = 11
                    ),
            'pencil': pyglet.window.ImageMouseCursor(
                pyglet.image.load(
                    os.path.join(data.filepath('theme'),'icons',
                    'draw-freehand.png')),
                    hot_x = 3, hot_y = 4
                    ),
            'eraser': pyglet.window.ImageMouseCursor(
                pyglet.image.load(
                    os.path.join(data.filepath('theme'),'icons',
                    'draw-eraser.png')),
                    hot_x = 11, hot_y = 11
                    ),
        }
    def update_mouse_cursor(self):
        if(self.active_tool in self.mouse_cursors):
            self.active_mouse_cursor = self.mouse_cursors[self.active_tool]
        else:
            self.active_mouse_cursor = self.mouse_cursors['default']

    
    def load_xml(self, level_xml):
        try:
            self.remove(self.manager)
            self.remove(self.dialog_layer)
            self.map_layer.walk(self.map_layer.remove)
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
            self.active_layer = layer
            mz = max(layer.origin_z, mz)
            mx = max(layer.px_width, mx)
            my = max(layer.px_height, my)

        self.level = level
        self.mx = mx
        self.my = my
        self.mz = mz
        self.add(self.dialog_layer,z = mz + 2)

        self.tilesets = []
        for id,t in level.findall(tiles.TileSet):
            self.tilesets.append(t)
#            print "id is %s"%id
#            print "t is %s"%t
#            print dir(t)
        self.reload_tileset()
        self.level_xml = level_xml
        self.level_edited = level
#        print self.tilesets

    def save_map(self):
        self.level_edited.save_xml(self.level_xml)
        
    def reload_tileset(self):
        if self.tilebar != None:
            self.tilebar.delete()
        self.active_tile = None
        self.tilebar = blobedit_dialogs.TileBarDialog(
            self.tilesets,
            on_select=self.on_tile_select,)
        self.dialog_layer.add_dialog(self.tilebar)
    def on_tile_select(self,data):
        self.active_tile = data
        print "Tile select %s"%data
        
def main():
    pyglet.font.add_directory(data.filepath('fonts'))
    pyglet.resource.path.append(data.filepath('.'))
    pyglet.resource.path.append(data.filepath('maps'))
    pyglet.resource.path.append(data.filepath('chars'))
    pyglet.resource.path.append(data.filepath('theme'))
    pyglet.resource.reindex()

    director.init(resizable=True, width=800, height=600, audio=None,do_not_scale=True)
    s = MapEditorScene()
    pyglet.gl.glClearColor(.3, .3, .3, 1)
    
    director.run( s )
