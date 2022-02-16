import socket

target_host = "127.0.0.1"
target_port = 9997

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Here the socket type is SOCK_DGRAM

# send some data - since UDP is connectionless, there's no need to call connect() before
client.sendto(b"AAABBBCCC",(target_host, target_port))

# receive some data
data, addr = client.recvfrom(4096) # this returns both the data AND the details of the remote host and port

print(data.decode())
client.close()
