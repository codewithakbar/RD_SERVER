import win32gui
import win32ui
import win32con
import win32api
import win32com.client
from PIL import Image
import io
import requests
import time
import argparse
import uuid

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

    print(f'Sending key "{key}" to server at {host}')

    r = requests.post(f'{host}/new_session', json={'_key': key})
    if r.status_code != 200:    
        print('Server not available.')
        return

    import asyncio
    asyncio.run(send_key_to_telegram(key))

    shell = win32com.client.Dispatch('WScript.Shell')
    PREV_IMG = None
    while True:
        hdesktop = win32gui.GetDesktopWindow()

        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        # device context
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)

        # memory context
        mem_dc = img_dc.CreateCompatibleDC()

        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        bmpinfo = screenshot.GetInfo()

        # copy into memory 
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top),win32con.SRCCOPY)

        bmpstr = screenshot.GetBitmapBits(True)

        pillow_img = Image.frombytes('RGB',
          (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
          bmpstr, 'raw', 'BGRX')

        with io.BytesIO() as image_data:
            pillow_img.save(image_data, 'PNG')
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
        
        # events
        try:
            r = requests.post(f'{host}/events_get', json={'_key': key})
            data = r.json()
            for e in data['events']:
                print(e)

                if e['type'] == 'click':
                    win32api.SetCursorPos((e['x'], e['y']))
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, e['x'], e['y'], 0, 0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, e['x'], e['y'], 0, 0)

                if e['type'] == 'keydown':
                    cmd = ''
                    
                    if e['shiftKey']:
                        cmd += '+'

                    if e['ctrlKey']:
                        cmd += '^'

                    if e['altKey']:
                        cmd += '%'

                    if len(e['key']) == 1:
                        cmd += e['key'].lower()
                    else:
                        cmd += '{'+e['key'].upper()+'}'

                    print(cmd)
                    shell.SendKeys(cmd)
                    
        except Exception as err:
            print(err)
            pass

        #screenshot.SaveBitmapFile(mem_dc, 'screen.bmp')
        # free
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        time.sleep(0.2)

if __name__ == '__main__':
    main()
