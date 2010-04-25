import pyglet.resource
from dialogs import *
import glob
import os
import sys
import data
from cocos.director import director
from kwidgets import *
import kytten

class OpenFileDialog(DialogNode):
    def __init__(self,dir,on_open=None):
        
        super(OpenFileDialog, self).__init__(kytten.FileLoadDialog(
            extensions=['.xml'], window=director.window,
            path = dir,
            theme=gTheme,
            on_select=self.on_open_click,
            on_escape=self.delete))

        self.selected_file = None
        self.on_open = on_open

    def on_level_file_select(self,file):
        print "level selected: ",file
        self.selected_file = file

    def on_level_file_cancel(self,data=None):
        print "level cancelled: ",data
        self.delete()
    def on_level_file_open(self,data = None):
        print "level to open: ",self.selected_file
        if self.selected_file != None:
            if(self.on_open != None):
                self.on_open(self.selected_file)
            self.delete()
    def on_open_click(self,data):
        print "level to open: ",data
        if(self.on_open != None):
            self.on_open(data)
        self.delete()


class ToolBarDialog(DialogNode):
    def __init__(self,on_tool_select = None,on_button_click=None):
        self.active_tool = 'move'
        if(on_tool_select == None):
            self.on_tool_select = None
        else:
            self.on_tool_select = on_tool_select
        if(on_button_click == None):
            self.on_button_click = None
        else:
            self.on_button_click = on_button_click

        toolbar_layout = self._get_tool_layout()
        file_layout = self._get_file_layout()
        super(ToolBarDialog, self).__init__(kytten.Dialog(
            kytten.Frame(
                kytten.Scrollable(
                    kytten.VerticalLayout([
                        kytten.FoldingSection('Tools',toolbar_layout),
                        kytten.FoldingSection('File', file_layout),
#                        kytten.FoldingSection('Map', map_menu_layout),
                    ], align=kytten.HALIGN_CENTER))
            ),
            window=director.window,
            anchor=kytten.ANCHOR_TOP_LEFT,
            theme=gTheme))
        self.help_texts = {
            'move'      : 'Move the map.',
            'zoom'      : 'Zoom in/out: use the mouse scroll.',
            'pencil'    : 'Use the pencil to draw tiles on the map.',
        }

    def get_help_text(self,id):
        if self.help_texts.has_key(id):
            text = self.help_texts[id]
        else:
            text = "%s - Not implemented"%id
        return text
    
    def _get_tool_layout(self):
        path = data.filepath('theme');
        path = os.path.join(path,'icons')

        images = [
            ('move',pyglet.image.load(
                os.path.join(path, 'transform-move.png'))),
            ('eraser',pyglet.image.load(
                os.path.join(path, 'draw-eraser.png'))),
            ('picker',pyglet.image.load(
                os.path.join(path, 'color-picker.png'))),
            ('zoom',pyglet.image.load(
                os.path.join(path, 'page-magnifier.png'))),
            ('pencil',pyglet.image.load(
                os.path.join(path, 'draw-freehand.png'))),
            ('fill',pyglet.image.load(
                os.path.join(path, 'color-fill.png'))),
        ]

        palette_options = [[],[],[]]
        for i,img in enumerate(images):
            option = PaletteOption(id = img[0], image = img[1], padding = 5)
            palette_options[i%3].append(option)

        layout = Palette(palette_options, on_select = self._on_tool_select)

        return layout

    def _get_file_layout(self):
        layout = kytten.VerticalLayout([
            NoSelectMenu(
                options     = ['-New', 'Open', 'Save', 'Quit'],
                on_select   = self._on_button_click
                )
#                    Button("Open",id ="open", on_click=self._on_button_click),
#                    Button("Save",id ="save", on_click=self._on_button_click),
#                    Button("Quit",id ="quit", on_click=self._on_button_click)
                ], align=kytten.HALIGN_LEFT)
        return layout

    def _on_button_click(self,id):
        print "clicked button <%s>"%id
        if(self.on_button_click != None):
            self.on_button_click(id)

    def _on_tool_select(self,id):
        print "selected tool %s"%id
        self.active_tool = id
        if(self.on_tool_select != None):
            self.on_tool_select(id)

class StatusBarDialog(DialogNode):
    def __init__(self):
        self.text = "Status"
        
        self.layout = self._get_layout()
        super(StatusBarDialog, self).__init__(kytten.Dialog(
            kytten.Frame(
                self.layout
                ),
                window=director.window,
                anchor=kytten.ANCHOR_BOTTOM_LEFT,
                theme=gTheme))
        

    def set_text(self,text):
        self.label.set_text(text)
    def _get_layout(self):
        self.label = Label(self.text)
        return kytten.HorizontalLayout([
                    self.label,
                ], align=kytten.HALIGN_LEFT)

class TileBarDialog(DialogNode):
    def __init__(self,tiles=None,on_select=None):
        self.tiles = tiles
        self.on_select = on_select
        self.layout = self._get_layout()
        self.active_tile = None
        super(TileBarDialog, self).__init__(kytten.Dialog(
            kytten.Frame(
                self.layout
                ),
                window=director.window,
                anchor=kytten.ANCHOR_BOTTOM,
                theme=gTheme))

    def _get_layout(self):
        images = []
        for tileset in self.tiles:
            print tileset
            for  id in tileset:
                tile = tileset[id]
                images.append(tile)


        palette_options = [[],[]]
        for i,tile in enumerate(images):
            option = PaletteOption(
                id = tile.id,
                image = tile.image,
                padding = 5,
                scale_size=20)
            palette_options[i%2].append(option)

        palette = Palette(palette_options, on_select = self._on_select)
        layout = kytten.Scrollable(palette)

        return layout
    def _on_select(self,data):
        print "selected %s"%data
        self.active_tile = data
        if self.on_select != None:
            self.on_select(data)
        
        
class PopupMessage(DialogNode):
    def __init__(self,text, ok = "Ok"):
        super(PopupMessage,self).__init__(
            kytten.PopupMessage(text,
                window = director.window,
                theme = gTheme,
        ))