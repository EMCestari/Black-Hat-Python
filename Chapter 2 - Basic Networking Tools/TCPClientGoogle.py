# This code snippet makes the following assumptions:
# 1) Our connection will always succeed
# 2) The server expects us to send data first (some servers expect to send data to you first and await your response).
# 3) The server will always return data to us in a timely fashion.
# While programmers have varied opinions about how to deal with blocking sockets, exception-handling in sockets, and the like, it’s quite rare for pentesters to build these niceties into their quick-and-dirty tools for recon or exploitation work, so we’ll omit them.

import socket

target_host = "www.google.com"
target_port = 80

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET parameter indicates we'll use a standard IPv4 address or host name
# SOCK_STREAM indicates this will be a TCP client

# connect the client
client.connect((target_host, target_port))

# send some data (as bytes)
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# receive some data
response = client.recv(4096)

print(response.decode())
client.close()
