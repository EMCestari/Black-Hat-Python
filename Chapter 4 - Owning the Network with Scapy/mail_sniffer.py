from scapy.all import sniff


def packet_callback(packet):
    print(packet.show())  # Callback function that receives each sniffed packet


def main():
    sniff(prn=packet_callback, count=1)  # Tells Scapy to sniff on all interfaces with no filtering


if __name__ == '__main__':
    main()
