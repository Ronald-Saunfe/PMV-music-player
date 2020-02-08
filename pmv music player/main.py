from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior, TouchRippleButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.label import Label
from kivy.uix.image import Image as ImageWidget
from kivy.uix.screenmanager import ScreenManager, CardTransition, SwapTransition, NoTransition,SlideTransition
from kivy.uix.carousel import Carousel
from kivy.uix.button import Button

from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty, StringProperty, ListProperty,\
     BoundedNumericProperty, NumericProperty, OptionProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import InstructionGroup, Color, Ellipse,\
                          Rectangle, RoundedRectangle, SmoothLine, Line

from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window

import re
import threading
import os
from kivy.clock import mainthread
import kivy
from kivy.core.window import Window
from kivy.metrics import dp, sp
from functools import partial
import glob
import socket
import pickle
import datetime
from requests import get
import ast
from array import array
import random
import smtplib
from PIL import Image, ImageDraw, ImageFilter
import kivy.properties as props
from os import walk
import mutagen
from mutagen.mp3 import MP3
from mutagen import File     
import math

RAD_MULT = 0.25 #  PIL GBlur seems to be stronger than Chrome's so I lower the radius

Window.size = (dp(360),dp(600))

class Audio_box(BoxLayout):
    duration = StringProperty('0:00')

class Sliders(BoxLayout):

    def __init__(self,**kwargs):
        super(Sliders, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        collide_point = self.collide_point(touch.x, touch.y)
        if collide_point:
            self.init_coord = touch.pos #get the initial coordinate
            return True
        return False
    
    def on_touch_move(self, touch):
        
        if self.collide_point(*touch.pos):

            if self.collide_point(*self.canvas.get_group('dark')[0].pos):
                self.changing_coord = touch.pos #get the changing coordinate
                #this is the center of the circle coordinates
                self.center_coord = self.canvas.get_group('light')[0].pos[0] +\
                                    self.canvas.get_group('light')[0].size[0]/2,\
                                    self.canvas.get_group('light')[0].pos[1] +\
                                    self.canvas.get_group('light')[0].size[1]/2

                
                #get sides of the triangle
                #side a
                y_a = self.changing_coord[1] - self.init_coord[1]
                x_a = self.changing_coord[0] - self.init_coord[0]
                val = (y_a**2 + x_a**2)
                side_a = math.sqrt(val)

                #side b
                y_b = self.center_coord[1] - self.init_coord[1]
                x_b = self.center_coord[0] - self.init_coord[0]
                val = (y_b**2 + x_a**2)
                side_b = math.sqrt(val)

                #side c
                y_c = self.init_coord[1] - self.center_coord[1]
                x_c = self.init_coord[0] - self.center_coord[0]
                val = (y_c**2 + x_c**2)
                side_c = math.sqrt(val)

                #use cosine rule to find the angle change
                upper_val = side_b**2 + side_c**2 - side_a**2
                lower_val = 2*side_b*side_c
                A = upper_val/lower_val

                try:
                    angle_change = math.acos(A)
                    self.canvas.get_group('light')[0].angle_start += angle_change
                    print(angle_change)
                except:
                    pass
                
            return True
        return False


class Object_details(TouchRippleButtonBehavior, BoxLayout):
    source = StringProperty()
    song_name = StringProperty()
    artsist_name = StringProperty()
    song_minutes = StringProperty('0:00')
    
    def on_touch_down(self, touch):
        collide_point = self.collide_point(touch.x, touch.y)
        if collide_point:
            self.elevation = 4
            self.ripple_fade_from_alpha =.8
            self.ripple_fade_to_alpha = .5
            self.ripple_scale = 1.5
            self.ripple_color = 1,1,1,1
            touch.grab(self)
            self.ripple_show(touch)

            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()

            for chld in self.parent.parent.children:
                chld.state = 'normal'

            self.parent.state = 'down'
            
            return True

            
        return False
    

class Track_items(ToggleButtonBehavior, BoxLayout):
    source = StringProperty()
    song_name = StringProperty()
    artsist_name = StringProperty()
    song_minutes = StringProperty('0:00')

    def __init__(self, **kwargs):
        super(Track_items, self).__init__(**kwargs)
       
    def on_state(self, widget, value):
        if value == 'down':
            #show audio box
            self.audio_box = Audio_box(size_hint_y = None, height = dp(60))
            self.height = dp(140)

            self.add_widget(self.audio_box)
        else:
            self.height = dp(64)
            self.remove_widget(self.audio_box)

    def on_press(self):
        self.state = 'down'

        
    
class MDLabel(Label):
    font_style = OptionProperty(
        'Caption', options=['Caption', 'Subhead', 'Title'])
    def __init__(self, **kwargs):
        super(MDLabel, self).__init__(**kwargs)


class Scrollview_tracks(BoxLayout):
    box = ObjectProperty()
    

class Pointer_ball(BoxLayout):
    text = StringProperty('#')
    
class Letter_widget(BoxLayout):
    
    def __init__(self, **kwargs):
        super(Letter_widget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 0,dp(8),0,dp(8)
        self.spacing = dp(5)

        #create letters
        self.label = MDLabel(text = '#', halign = 'center',\
                             color = (1,1,1,.4))
        self.label.text_size = self.label.size
        self.add_widget(self.label)
        for i in range(ord('A'), ord('Z')+1):
            self.label = MDLabel(text = chr(i), halign = 'center',\
                             color = (1,1,1,.4))
            self.label.text_size = self.label.size
            self.add_widget(self.label)

        #create a pointer
        self.float = FloatLayout(size_hint_y = None, height = dp(1))
        self.add_widget(self.float)
        
        self.pointer = Pointer_ball(pos_hint= {'right':1})
        self.float.add_widget(self.pointer)
        
    def on_touch_move(self, touch):
        #check first if collision is happening within the widget
        if self.collide_point( *touch.pos ):
            #show the pointer
            self.pointer.opacity =1
            self.pointer.y = touch.y
            #set pointer letters
            for chld in self.children:
                if chld.collide_point(*touch.pos):
                    try:
                        self.pointer.text = chld.text

                        for child_win in self.parent.parent.box.children:
                            song_name = child_win.song_name.lower()
                            if song_name[0] == self.pointer.text.lower():
                                self.parent.parent.box.parent.scroll_to(child_win)

                    except:
                        pass
              
        return super(Letter_widget, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        anim = Animation(opacity = 0)
        Clock.schedule_once(lambda x:anim.start(self.pointer),.6)
        
        return super(Letter_widget, self).on_touch_up(touch)


    
class MDSeparator(BoxLayout):
    color = ListProperty([0,0,0,.15])
    """ A separator line """
    def __init__(self, *args, **kwargs):
        super(MDSeparator, self).__init__(*args, **kwargs)
        self.on_orientation()
    
    def on_orientation(self,*args):
        self.size_hint = (1, None) if self.orientation == 'horizontal' else (None, 1)
        if self.orientation == 'horizontal':
            self.height = dp(1)
        else:
            self.width = dp(1)

            
class Circle_clickabe_image(ButtonBehavior, ImageWidget):
    source= ObjectProperty()
    color_up = ListProperty()
    color_down = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point( *touch.pos ):
            self.canvas.before.get_group('a')[0].rgba = self.color_down
        return super(Circle_clickabe_image, self).on_touch_down(touch)
 
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.canvas.before.get_group('a')[0].rgba = self.color_up
        return super(Circle_clickabe_image, self).on_touch_up(touch)


class Body(ScreenManager):
    scrll_track = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        #load music files
        threading.Thread(target = self.load_tracks, args =()).start()

    def load_tracks(self, *args):
        f = []
        mypath = 'C:/downloads for d/Music/'
       
        for (dirpath, dirnames, filenames) in walk(mypath):
            file_names = filenames
            break

        
        for filename in file_names:
            #get the album art
            file = File(mypath+filename)

            if 'APIC' in file:
                try:
                    artwork = file.tags['APIC:'].data # access APIC frame and grab the image
                    with open('album_arts/%s.jpg'%filenames, 'wb') as img:
                       img.write(artwork) # write artwork to new image
                    img_path = 'album_arts/%s.jpg'%filename
                except:
                    img_path = 'pics/track.png'
            else:
                img_path = 'pics/track.png'

            #get the duration of the song
            audio = MP3(mypath+filename)
            
            details = mutagen.File(mypath+filename)
            
            if 'title' in details:
                try:
                    song_name = details['title']
                except:
                    song_name = filename[:-4]
            else:
                song_name = filename[:-4]

            if 'artist' in details:
                try:
                    artist = details['artist']
                except:
                    artist = ''
            else:
                artist = ''

            try:
                song_minutes = str(audio.info.length/60)[:4].replace('.',':')
                
            except:
                song_minutes = '0:00'

            self.add_widgets_1(img_path, song_name, artist, song_minutes)

    @mainthread
    def add_widgets_1(self, img_path, song_name, artist, song_minutes, *args):
        self.track_items = Track_items(size_hint_y =None, height = dp(70),\
                                       source = img_path,\
                                       song_name = song_name,\
                                       artsist_name = artist,\
                                       song_minutes = str(song_minutes))

        self.ids.scrll_track.ids.box.add_widget(self.track_items)
            
            
        
        
class ShadowBehavior(TouchRippleButtonBehavior, object):
    shadow_texture1 = props.ObjectProperty(None)
    shadow_pos1 = props.ListProperty([0, 0])
    shadow_size1 = props.ListProperty([0, 0])

    shadow_texture2 = props.ObjectProperty(None)
    shadow_pos2 = props.ListProperty([0, 0])
    shadow_size2 = props.ListProperty([0, 0])

    elevation = props.NumericProperty(1)

    _shadows = {
        1: (1, 3, 0.12, 1, 2, 0.24),
        2: (3, 6, 0.16, 3, 6, 0.23),
        3: (10, 20, 0.19, 6, 6, 0.23),
        4: (14, 28, 0.25, 10, 10, 0.22),
        5: (19, 38, 0.30, 15, 12, 0.22)
    }

    # Shadows for each elevation.
    # Each tuple is: (offset_y1, blur_radius1, color_alpha1, offset_y2, blur_radius2, color_alpha2)
    # The values are extracted from the css (box-shadow rule).

    def __init__(self, *args, **kwargs):
        super(ShadowBehavior, self).__init__(*args, **kwargs)
        self._update_shadow = _us = Clock.create_trigger(self._create_shadow)
        self.bind(size=_us, pos=_us, elevation=_us)

    def _create_shadow(self, *args):
        # print "update shadow"
        ow, oh = self.size[0], self.size[1]

        offset_x = 0

        # Shadow 1
        shadow_data = self._shadows[self.elevation]
        offset_y = shadow_data[0]
        radius = shadow_data[1]
        w, h = ow + radius * 6.0, oh + radius * 6.0
        t1 = self._create_boxshadow(ow, oh, radius, shadow_data[2])
        self.shadow_texture1 = t1
        self.shadow_size1 = w, h
        self.shadow_pos1 = self.x - \
            (w - ow) / 2. + offset_x, self.y - (h - oh) / 2. - offset_y

        # Shadow 2
        shadow_data = self._shadows[self.elevation]
        offset_y = shadow_data[3]
        radius = shadow_data[4]
        w, h = ow + radius * 6.0, oh + radius * 6.0
        t2 = self._create_boxshadow(ow, oh, radius, shadow_data[5])
        self.shadow_texture2 = t2
        self.shadow_size2 = w, h
        self.shadow_pos2 = self.x - \
            (w - ow) / 2. + offset_x, self.y - (h - oh) / 2. - offset_y

    def _create_boxshadow(self, ow, oh, radius, alpha):
        # We need a bigger texture to correctly blur the edges
        w = ow + radius * 6.0
        h = oh + radius * 6.0
        w = int(w)
        h = int(h)
        texture = Texture.create(size=(w, h), colorfmt='rgba')
        im = Image.new('RGBA', (w, h), color=(1, 1, 1, 0))

        draw = ImageDraw.Draw(im)
        # the rectangle to be rendered needs to be centered on the texture
        x0, y0 = (w - ow) / 2., (h - oh) / 2.
        x1, y1 = x0 + ow - 1, y0 + oh - 1
        draw.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, int(255 * alpha)))
        im = im.filter(ImageFilter.GaussianBlur(radius * RAD_MULT))
        texture.blit_buffer(im.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        return texture

class All_tracks(BoxLayout):
    pass

class Recently_added_songs(ShadowBehavior, BoxLayout):
    source = StringProperty()
    text = StringProperty()

    def on_touch_down(self, touch):
        collide_point = self.collide_point(touch.x, touch.y)
        if collide_point:
            self.elevation = 4
            self.ripple_fade_from_alpha =.8
            self.ripple_fade_to_alpha = .5
            self.ripple_scale = 1.5
            self.ripple_color = .46, .32, .43, 1
            touch.grab(self)
            self.ripple_show(touch)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.elevation = 2
            touch.ungrab(self)
            self.ripple_fade()
            return True
        return False


class MainApp(App):
    def build(self):
        
        return Body()

if __name__=='__main__':
    MainApp().run()


    
