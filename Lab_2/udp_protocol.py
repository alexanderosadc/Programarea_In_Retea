import socket
import hashlib
import json
import random as rand
from pprint import pprint
from cryptography.fernet import Fernet
from hashlib import scrypt
from base64 import urlsafe_b64decode

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

    def make_packet(self, message, packet, ack_flag, host_to_send, port_to_send):
        packet.header['host_to_send'] = host_to_send
        packet.header['port_to_send'] = port_to_send
        packet.header['message'] = message
        packet.header['ack_flag'] = ack_flag
        packet.header['checksum'] = hashlib.md5(message.encode('utf-8')).hexdigest()

        return packet

    def transform_to_bytes(self) -> bytes:
        return bytes(json.dumps(self.header).encode('utf-8'))

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
        self.private_key = rand.randint(1, 100)





    # Server and Client
    def receive_data(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))
            self.host_to_send = recieved_packet['current_host']
            self.port_to_send = recieved_packet['current_port']
            message_decrypted = self.decrypt_message(recieved_packet['message'])
                # Client
                # If flag aknowledgment is risen that the message sent from SERVER to the CLIENT
            if recieved_packet['ack_flag']:
                print(message_decrypted)
                self.recieve_message_client(recieved_packet, message_decrypted)
                if self.retransmission_number >= 5:
                    print('Server error. Stop sending data')
                    break
            else:
                # Server
                    # If flag aknowledgment is not risen that this is the SERVER
                self.recieve_message_server(recieved_packet, message_decrypted)


    def recieve_message_client(self, recieved_packet, message_decrypted):
        if message_decrypted == 'NACK':
            self.send(self.current_sent_packet.header['message'], False)
            self.retransmission_number += 1
        elif message_decrypted == 'ACK':
            self.retransmission_number = 0

    def recieve_message_server(self, recieved_packet, message_decrypted):
        message_cheksum = hashlib.md5(message_decrypted.encode('utf-8')).hexdigest()
        print(recieved_packet['message'])
        if recieved_packet['checksum'] != message_cheksum:
            self.send('NACK', True)
        else:
            self.send('ACK', True)


    def ecnrypt_message(self, message):

        encrypted_message = ''
        for i in range(0, len(message)):
            position = ord(message[i]) + self.private_key
            if position > 127:
                position = 127 - self.private_key
            elif position < 0:
                position = self.private_key
            encrypted_message += encrypted_message + chr(position)
        return encrypted_message

    def decrypt_message(self, message):

        encrypted_message = ''
        for i in range(0, len(message)):
            position = ord(message[i]) - self.private_key
            if position > 127:
                position = position - 127
            elif position < 0:
                position = 127 - position
            encrypted_message += encrypted_message + chr(position)
        print(encrypted_message)
        return encrypted_message

    def send(self, message, ack_flag):
        packet = Packet()
        packet.header['current_host'] = self.current_host
        packet.header['current_port'] = self.current_port

        encrypted_message = self.ecnrypt_message(message)
        self.current_sent_packet = packet.make_packet(encrypted_message, packet, ack_flag, self.host_to_send, self.port_to_send)
        packet_in_bytes = packet.transform_to_bytes()
        to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        self.sock.sendto(packet_in_bytes, to_address)
