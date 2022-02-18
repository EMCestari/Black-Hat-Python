import sys
import socket
import threading

## HEX_FILTER is a string that conains ASCII printable characters, if one exists, or a dot
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])


## hexdump takes some inputs as bytes or a string and prints a hexdump to the console
## It will output the packet details with both their hexadecimal values and ASCII-printable characters
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode() ## We ensure we have a string

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length]) ## We take a piece of the string to dump and put it into word

        printable = word.translate(HEX_FILTER) ## We substitute the string representation of each character for the corresponding character
        hexa = ' '.join([f'{ord(c):02X}' for c in word]) ## We substitute the hex representation of the integer value of every character in the raw string
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}') ## We create a new array to hold the string
    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    buffer = b"" ## We create an empty byte string to accumulate responses from the socket.
    connection.settimeout(10) ## 5 second could be aggressive as a timeout, to be increased if needed
    try:
        while True: ## We set up a loop to read response data into buffer
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    # perform packet modifications
    return buffer


def response_handler(buffer):
    # perform packet modifications
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host,local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target = proxy_handler,
            args=(client_socket, remote_host,
                  remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()