import socket

class BackdoorClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f'Serverga {self.host}:{self.port} da ulandi.')
        except Exception as e:
            print(f'Ulanish muvaffaqiyatsiz: {e}')
            self.client_socket.close()
            return False
        return True

    def send_command(self, command):
        try:
            self.client_socket.sendall(command.encode())  # Serverga buyruq yuborish
            data = self.client_socket.recv(4096)  # Serverdan javobni qabul qilish
            return data.decode()
        except Exception as e:
            return f'Xato yuz berdi: {e}'

    def close(self):
        self.client_socket.close()
        print('Aloqa uzildi.')

# Mijozni ishga tushirish
if __name__ == "__main__":
    client = BackdoorClient()
    if client.connect():
        while True:
            command = input("Buyruqni kiriting: ")
            if command.lower() == 'exit':
                break
            response = client.send_command(command)
            print('Serverdan kelgan natija:')
            print(response)
        client.close()
