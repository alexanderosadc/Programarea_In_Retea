import socket
import hashlib
import json
import random as rand
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
            'message': '',
            'public_key_n': 0,
            'public_key_g': 0,
            'handshake': False,
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
        self.private_key = rand.randint(100, 1000)


    def generate_secret_formula(self, public_key_g, public_key_n, sent_private_key, last_verification):
        print("g=" + str(public_key_g))
        print("n=" + str(public_key_n))
        print("private_key=" + str(self.private_key))
        print("sent_private_key=" + str(sent_private_key))
        if sent_private_key == -1:
            print('First Time')
            self.private_key = pow(public_key_g, self.private_key, public_key_n)
        elif last_verification:
            self.private_key = pow(self.private_key, sent_private_key, public_key_n)
        else:
            print('Second Time')
            self.private_key = pow(sent_private_key, self.private_key, public_key_n)
            print(self.private_key)

    def send_handshake_client(self):
        packet = Packet()
        packet.header['public_key_n'] = rand.randint(100, 1000)
        packet.header['public_key_g'] = rand.randint(100, 1000)
        self.generate_secret_formula(packet.header['public_key_g'], packet.header['public_key_n'], -1, False)
        # self.security_key = int(pow(packet.header['public_key_g'], self.private_key, packet.header['public_key_n']))
        # packet.header['message'] = self.security_key
        self.send_hadnshake(packet)
        # packet_in_bytes = self.make_packet(str(self.security_key), packet, False)
        # to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        # self.sock.sendto(packet_in_bytes, to_address)


    def recieve_handshake_server(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))
            if self.retransmission_number < 1:

                self.host_to_send = recieved_packet['current_host']
                self.port_to_send = recieved_packet['current_port']

                packet = Packet()
                packet.header['public_key_g'] = recieved_packet['public_key_g']
                packet.header['public_key_n'] = recieved_packet['public_key_n']

                self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'], -1, False)
                self.send_hadnshake(packet)
                self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'], int(recieved_packet['message']), True)
            else:
                print(str(self.private_key))
                break


    def send_hadnshake(self, packet):
        packet.header['current_host'] = self.current_host
        packet.header['current_port'] = self.current_port
        packet_in_bytes = self.make_packet(str(self.private_key), packet, False)
        to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        self.sock.sendto(packet_in_bytes, to_address)
        self.retransmission_number += 1

    def recieve_handshake_client(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))
            self.host_to_send = recieved_packet['current_host']
            self.port_to_send = recieved_packet['current_port']

            self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'],
                                         int(recieved_packet['message']), False)

            packet = Packet()
            packet.header['public_key_g'] = recieved_packet['public_key_g']
            packet.header['public_key_n'] = recieved_packet['public_key_n']
            self.send_hadnshake(packet)
            print(self.private_key)
            break

    #Client
    def connect_to_addr(self, host, port):
        self.host_to_send = host
        self.port_to_send = port
        self.send_handshake_client()

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
            self.host_to_send = recieved_packet['current_host']
            self.port_to_send = recieved_packet['current_port']

                # Client
                # If flag aknowledgment is risen that the message sent from SERVER to the CLIENT
            if recieved_packet['ack_flag']:
                print(recieved_packet['message'])
                self.recieve_message_client(recieved_packet)
                if self.retransmission_number >= 5:
                    print('Server error. Stop sending data')
                    break
            else:
                # Server
                    # If flag aknowledgment is not risen that this is the SERVER
                self.recieve_message_server(recieved_packet)


    def recieve_message_client(self, recieved_packet):
        if recieved_packet['message'] == 'NACK':
            self.send(self.current_sent_packet.header['message'], False)
            self.retransmission_number += 1
        elif recieved_packet['message'] == 'ACK':
            self.retransmission_number = 0

    def recieve_message_server(self, recieved_packet):
        message_cheksum = hashlib.md5(recieved_packet['message'].encode('utf-8')).hexdigest()

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
