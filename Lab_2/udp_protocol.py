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
        self.retransmission_number = 0

class Socket:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.host_to_send = 0
        self.port_to_send = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.current_sent_packet = Packet()


    def make_packet(self, message, packet, ack_flag) -> bytes:

        packet.header['host_to_send'] = self.host_to_send
        packet.header['port_to_send'] = self.port_to_send
        packet.header['message'] = message
        packet.header['ack_flag'] = ack_flag
        packet.header['checksum'] = hashlib.md5(message.encode('utf-8')).hexdigest()
        self.current_sent_packet = packet

        return bytes(json.dumps(packet.header).encode('utf-8'))

    def connect_to_addr(self, host, port):
        self.host_to_send = host
        self.port_to_send = port
        print(self.host_to_send)

    def receive(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))
            message_cheksum = hashlib.md5(recieved_packet['message'].encode('utf-8')).hexdigest()
            ack_flag = recieved_packet['ack_flag']
                #Client
            # If flag aknowledgment is risen that the message sent from SERVER to the CLIENT
            if recieved_packet['ack_flag']:
                if recieved_packet['message'] == 'NACK':
                    pprint('NACK')
                    self.send(self.current_sent_packet.header['message'], False)
                    self.current_sent_packet.retransmission_number += 1
                    if self.current_sent_packet.retransmission_number > 5:
                        print('Server error. Stop sending data')
                        break
                elif recieved_packet['message'] == 'ACK':
                    self.current_sent_packet.retransmission_number = 0
                    pprint(recieved_packet)
            else:
                #Server
                #If flag aknowledgment is not risen that this is the SERVER
                self.host_to_send = recieved_packet['current_host']
                self.port_to_send = recieved_packet['current_port']
                if recieved_packet['checksum'] != message_cheksum:
                    self.send('NACK', True)
                else:
                    # recieved_packet['ack_flag'] = False
                    self.send('ACK', False)
                    pprint(recieved_packet)

    def send(self, message, ack_flag):
        packet = Packet()
        packet_in_bytes = self.make_packet(message, packet, ack_flag)
        to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        self.sock.sendto(packet_in_bytes, to_address)