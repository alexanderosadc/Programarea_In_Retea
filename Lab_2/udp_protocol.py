import socket
import hashlib
import json
from pprint import pprint

BUFF_SIZE = 1024


class Packet:
    def __init__(self, host='localhost', port=8080):
        self.header = {
            'current_host': host,
            'current_port': port,
            'host_to_send': 0,
            'port_to_send': 0,
            'checksum': '',
            'ack_flag': False,
            'message': ''
        }


class Socket:
    def __init__(self, host='localhost', port=8080):
        self.current_host = host
        self.current_port = port
        self.host_to_send = 0
        self.port_to_send = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.current_sent_packet = Packet()
        self.retransmission_number = 0

    #Client
    def connect_to_addr(self, host, port):
        self.host_to_send = host
        self.port_to_send = port

    # Client and Server
    def make_packet(self, message, packet, ack_flag) -> bytes:

        packet.header['host_to_send'] = self.host_to_send
        packet.header['port_to_send'] = self.port_to_send
        packet.header['message'] = message
        packet.header['ack_flag'] = ack_flag
        packet.header['checksum'] = hashlib.md5(message.encode('utf-8')).hexdigest()
        self.current_sent_packet = packet

        return bytes(json.dumps(packet.header).encode('utf-8'))

    # Server and Client
    def receive_data(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))

            # Client
            # If flag aknowledgment is risen that the message sent from SERVER to the CLIENT
            if recieved_packet['ack_flag']:
                print(recieved_packet['message'])
                self.recieve_data_client(recieved_packet)
                if self.retransmission_number >= 5:
                    print('Server error. Stop sending data')
                    break
            else:
                # Server
                # If flag aknowledgment is not risen that this is the SERVER
                self.recieve_data_server(recieved_packet)


    def recieve_data_client(self, recieved_packet):
        if recieved_packet['message'] == 'NACK':
            self.send(self.current_sent_packet.header['message'], False)
            self.retransmission_number += 1
        elif recieved_packet['message'] == 'ACK':
            self.retransmission_number = 0

    def recieve_data_server(self, recieved_packet):
        message_cheksum = hashlib.md5(recieved_packet['message'].encode('utf-8')).hexdigest()
        self.host_to_send = recieved_packet['current_host']
        self.port_to_send = recieved_packet['current_port']

        if recieved_packet['checksum'] != message_cheksum:
            self.send('NACK', True)
        else:
            self.send('ACK', True)

    def send(self, message, ack_flag):
        packet = Packet()
        packet.header['current_host'] = self.current_host
        packet.header['current_port'] = self.current_port

        packet_in_bytes = self.make_packet(message, packet, ack_flag)
        to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        self.sock.sendto(packet_in_bytes, to_address)
