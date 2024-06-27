import socket
import subprocess
import threading

class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'Server {self.host}:{self.port} da tinglamoqda...')

    def handle_client(self, conn, addr):
        print(f'Ulanish amalga oshirildi: {addr}')
        with conn:
            while True:
                command = conn.recv(1024)  # Mijozdan buyruq qabul qilish
                if not command:
                    break
                command = command.decode()
                print(f'Mijozdan kelgan buyruq: {command}')

                # Buyruqni bajarish
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                except Exception as e:
                    output = str(e)

                conn.sendall(output.encode())  # Natijani mijozga qaytarish

    def start(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()  # Ulanuvchini qabul qilish
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
        finally:
            self.server_socket.close()

# Serverni ishga tushirish
if __name__ == "__main__":
    server = TCPServer()
    server.start()
