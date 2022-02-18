import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    ## We use subprocess library, which provides a process-creation interface to interact with client programs
    output = subprocess.check_output(shlex.split(cmd), ## check_output method runs a command on the local operating system and returns the output from that command.
                                     stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    def __init__(self, args, buffer=None): ## We initialize the NetCat object with the arguments from the command line and the buffer
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ## We create the socket object
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen() ## If we're setting up a listener, we call the listen method...
        else:
            self.send() ## ... otherwise, the send method

    def send(self):
        self.socket.connect((self.args.target, self.args.port)) ## We connect to the target and port
        if self.buffer:
            self.socket.send(self.buffer) ## If we have a buffer, we send it first

        try: ## This try/catch block is used to allow to manually close the connection with CTRL-C
            while True: ## We start a loop to receive data from the target
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break ## If there's no more data, we break out of the loop
                if response:
                    print(response)
                    buffer = input('> ') ## We pause to get interactive input
                    buffer += '\n'
                    self.socket.send(buffer.encode()) ## We send the input
        except KeyboardInterrupt: ## loop will continue until CTRL-C is pressed
            print('User terminated.')
            self.socket.close()
            sys.exit()


    def listen(self):
        self.socket.bind((self.args.target, self.args.port)) ## Binds to the target and port
        self.socket.listen(5) ## Starts listening in a loop
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread( ## Passes the connected socket to the handle method
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()


    def handle(self, client_socket): ## Handle method executes the task corresponding to the command line argument it receives
        if self.args.execute: ## if a command should be executed
            output = execute(self.args.execute) ## asses that command to the execute function
            client_socket.send(output.encode()) ## sends the output back on the socket

        elif self.args.upload: ## If a file should be uploaded
            file_buffer = b''
            while True:
                data = client_socket_recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())

        elif self.args.command: ## If a shell is to be created
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser( # We use the argparse module to create a command line interface
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        ## We provide example usage that the program will display when the user invokes it with --help
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server
            netcat.py .t 192.168.1.108 -p 5555 # connect to server
        '''))
    ## We add six arguments that specify how we want the program to behave.
    parser.add_argument('-c', '--command', action='store_true', help='command shell') ## -c argument sets up an interactive shell
    parser.add_argument('-e', '--execute', help='execute specified command') ## -e argument executes one specific command
    parser.add_argument('-l', '--listen', action='store_true', help='listen') ## -l argument indicates that a listener should be set up
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port') ## -p argument specifies the port on which to communicate
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP') ## - t argument specifies the target IP
    parser.add_argument('-u', '--upload', help='upload file') ## -u argument specifies the name of a file to upload
    args = parser.parse_args()
    if args.listen:
        buffer = '' ## If setting it up as listener, the buffer string is empty
    else:
        buffer = sys.stdin.read() ## Otherwise, we send the buffer content from stdin

    nc = NetCat(args, buffer.encode()) ## We invoke the NetCat object
    nc.run() ## We run it