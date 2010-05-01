
# original file from http://www.partiallydisassembled.net/make_me/
# modified later for this game

import pyglet
#
# MUSIC
# 
#pyglet.options["audio"] = ('openal',)
music_player = pyglet.media.Player()

current_music = None

sound_vol = 0.7
music_player.volume = 0.4

def set_music(name):
    global current_music

    if name == current_music:
        return
    current_music = name


    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    # pyglet bug
    music_player.volume = music_player.volume
    music_player.play()
    music_player.eos_action = 'loop'

def music_volume(vol):
    global music_player
    if(vol):
        music_player.volume = vol
    return music_player.volume

def queue_music(name):
    global current_music

    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.eos_action = 'next'


def play_music():
    if music_player.playing or not current_music:
        return

    name = current_music
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

@music_player.event
def on_eos():
    music_player.eos_action = 'loop'


def stop_music():
    music_player.pause()

#
# SOUND
#
sounds = {}

def load(name, streaming=False):
    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=streaming)
    return sounds[name]

def play(name):
    load(name)
    a = sounds[name]
    a.volume = sound_vol
    a.play()

def sound_volume( vol = None ):
    global sound_vol
    if(vol):
        sound_vol = vol
    return sound_vol

