from threading import Thread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.base import runTouchApp
from kivy.config import Config
import sys
import os
import time
import requests
from PIL import ImageGrab
from io import BytesIO

import mss
import io

from kivy.app import App
from kivy.lang import Builder

Config.set('graphics', 'multisamples', '0')

class Main(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class MainApp(App):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        # Start the screen capture in a new thread
        Thread(target=self.capture_and_send, daemon=True).start()
        return kv
   
def take_screenshot():
    # Takes screenshot of screen
    with ImageGrab.grab() as im:
        # Converts to BytesIO
        with BytesIO() as png:
            im.save(png, 'PNG')
            return png.getvalue()

def capture_and_send(self):
        PREV_IMG = None
        host = 'http://192.168.50.50:5000'  # Replace with your actual host address
        key = '1112'  # Replace with your actual key

        with mss.mss() as sct:
            while True:
                # Get the size of the primary monitor
                monitor = sct.monitors[1]
                
                # Capture the screen
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

                # Save the image to a bytes buffer
                with io.BytesIO() as image_data:
                    img.save(image_data, 'PNG')
                    image_data_content = image_data.getvalue()

                # Check if the image has changed
                if image_data_content != PREV_IMG:
                    files = {}
                    filename = str(round(time.time() * 1000)) + '_' + key
                    files[filename] = ('img.png', image_data_content, 'multipart/form-data')

                    try:
                        # Send the image to the host
                        r = requests.post(f'{host}/capture_post', files=files)
                        r.raise_for_status()
                        print(f'Image sent: {filename}')
                    except requests.exceptions.RequestException as e:
                        print(f'Error sending image: {e}')

                    # Update the previous image
                    PREV_IMG = image_data_content
                else:
                    print('No desktop change')

                # Wait before capturing the next frame
                time.sleep(0.1)

# Create the root widget
kv = Builder.load_string('''
WindowManager:
    Main:
<Main>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'WebView App'
            size_hint_y: None
            height: '48dp'
        Button:
            text: 'Take Screenshot and Send'
            on_release: app.take_and_send_screenshot()
''')

class MyApp(App):
    def build(self):
        return kv

    def take_and_send_screenshot(self):
        take_screenshot()

if __name__ == '__main__':
    MyApp().run()
