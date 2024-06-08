import webview

def main():
    webview.create_window('Simple Webview App', 'https://www.utu-ranch.uz')

    # Start the webview loop
    webview.start()

if __name__ == '__main__':
    main()
