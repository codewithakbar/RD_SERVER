import socket
import time
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import io
import requests
import win32com.client

def capture_screen():
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
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    bmpstr = screenshot.GetBitmapBits(True)

    pillow_img = Image.frombytes('RGB',
                                 (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                 bmpstr, 'raw', 'BGRX')

    with io.BytesIO() as image_data:
        pillow_img.save(image_data, 'PNG')
        image_data_content = image_data.getvalue()

    # free
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

    return image_data_content

def start_client(host='127.0.0.1', port=65432):
    PREV_IMG = None
    shell = win32com.client.Dispatch('WScript.Shell')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        while True:
            try:
                current_img = capture_screen()
                if current_img != PREV_IMG:
                    files = {}
                    filename = str(round(time.time()*1000)) + '_screenshot'
                    files[filename] = ('img.png', current_img, 'multipart/form-data')

                    try:
                        r = requests.post(f'http://{host}:8000/capture_post', files=files)
                    except Exception as e:
                        print(f"Error posting screenshot: {e}")

                    PREV_IMG = current_img
                else:
                    pass  # No desktop change detected

                time.sleep(0.1)
            except Exception as err:
                print(f"Error: {err}")
                pass

if __name__ == "__main__":
    start_client()
