import socket
import threading

IP = '0.0.0.0'
PORT = 9998


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT)) # We pass the IP address and port we want the server to LISTEN ON
    server.listen(5) # We tell the server to start listening, with a maximum backlog of connections set to 5
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept() # When a client connects, we receive the client socket in the client variable and the remote connection details in the address variable
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,)) # We create a new thread object that points to handle_client function, passing the client socket object as argument
        client_handler.start() # We start the thread to handle client connection


def handle_client(client_socket): ## This function performs the recv() and just sends a simple message back to the client
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':
    main()
