import socket
import os

# host to listen to
HOST = '192.168.56.1'


def main():
    # create raw socket, bin to public interface
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol) # We build our socket object with the parameters necessary for sniffing packets on our network interface.
    sniffer.bind((HOST, 0))
    # include the IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1) # We set a socket option that includes the IP headers in our capture packets.

    if os.name == 'nt':  # It determines if we are using Windows
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON) # In Windows case, it performs an additional step of sending an IOCTL to the network card driver to enable promiscuous mode.

    # read one packet
    print(sniffer.recvfrom(65565)) # At this point we just sniff and print the raw packet

    # if we're on Windows, turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()
