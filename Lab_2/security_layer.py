from udp_protocol import Packet, BUFF_SIZE
import json
import random as rand
from udp_protocol import Packet, Socket


class Security(Socket):

    def __init__(self, host, port):
        Socket.__init__(self, host, port)

    def connect_to_addr(self, host, port):
        self.host_to_send = host
        self.port_to_send = port
        self.send_handshake_client()

    def generate_secret_formula(self, public_key_g, public_key_n, sent_private_key, last_verification):
        if sent_private_key == -1:
            self.private_key = pow(public_key_g, self.private_key, public_key_n)
        elif last_verification:
            self.private_key = pow(self.private_key, sent_private_key, public_key_n)
        else:
            self.private_key = pow(sent_private_key, self.private_key, public_key_n)

    def send_handshake_client(self):
        packet = Packet()
        packet.header['public_key_n'] = rand.randint(100, 1000)
        packet.header['public_key_g'] = rand.randint(100, 1000)
        self.generate_secret_formula(packet.header['public_key_g'], packet.header['public_key_n'], -1, False)
        self.send_hadnshake(packet)

    def recieve_handshake_server(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))

            self.host_to_send = recieved_packet['current_host']
            self.port_to_send = recieved_packet['current_port']
            self.public_key = recieved_packet['public_key_g']

            packet = Packet()
            packet.header['public_key_g'] = recieved_packet['public_key_g']
            packet.header['public_key_n'] = recieved_packet['public_key_n']

            if self.retransmission_number < 1:

                self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'], -1,
                                             False)
                self.send_hadnshake(packet)
                self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'],
                                             int(recieved_packet['message']), True)
            else:
                if self.private_key == int(recieved_packet['message']):

                    packet.header['handshake'] = True
                    self.send_hadnshake(packet)
                    self.retransmission_number = 0
                    self.receive_data()

                else:
                    print('Handshake is not happening')
                break

    def send_hadnshake(self, packet):
        packet.header['current_host'] = self.current_host
        packet.header['current_port'] = self.current_port
        self.current_sent_packet = packet.make_packet(str(self.private_key), packet, False, self.host_to_send,
                                                      self.port_to_send)
        packet_in_bytes = packet.transform_to_bytes()
        to_address = (packet.header['host_to_send'], packet.header['port_to_send'])
        self.sock.sendto(packet_in_bytes, to_address)
        self.retransmission_number += 1

    def recieve_handshake_client(self):
        while True:
            data, addr = self.sock.recvfrom(BUFF_SIZE)
            recieved_packet = json.loads(data.decode('utf-8'))
            if not recieved_packet['handshake']:
                self.public_key = recieved_packet['public_key_g']
                self.host_to_send = recieved_packet['current_host']
                self.port_to_send = recieved_packet['current_port']

                self.generate_secret_formula(recieved_packet['public_key_g'], recieved_packet['public_key_n'],
                                             int(recieved_packet['message']), False)

                packet = Packet()
                packet.header['public_key_g'] = recieved_packet['public_key_g']
                packet.header['public_key_n'] = recieved_packet['public_key_n']

                self.send_hadnshake(packet)
            else:
                self.send('Alex', False)
                self.receive_data()
                break