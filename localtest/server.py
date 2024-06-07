import socket

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")
    return server_socket

def receive_message(client_socket):
    message = client_socket.recv(1024).decode()
    return message

def close_connection(client_socket):
    client_socket.close()

def main():
    HOST = '127.0.0.1'  # Change this to the IP address you want to listen on, or use '0.0.0.0' to listen on all available network interfaces
    PORT = 12345        # Change this to the port number you want to listen on
    server_socket = start_server(HOST, PORT)
    
    while True:
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        try:
            message = receive_message(client_socket)
            print(f"Received message from client: {message}")
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
        
        close_connection(client_socket)

if __name__ == "__main__":
    main()
