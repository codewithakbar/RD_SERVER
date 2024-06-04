import socket
import threading

def handle_client(client_socket):
    while True:
        try:
            command = input("Enter command to send to client: ")
            if command.lower() == 'exit':
                client_socket.send(command.encode('utf-8'))
                break
            client_socket.send(command.encode('utf-8'))
            response = client_socket.recv(4096).decode('utf-8')
            print(f"Response from client:\n{response}")
        except Exception as e:
            print(f"Connection lost: {e}")
            break
    client_socket.close()

def start_server(host='192.168.50.50', port=65432):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
