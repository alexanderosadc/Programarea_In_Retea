# Programarea_In_Retea
## Laboratory Work Nr 1
### General Info
The scope of the project is to parse data, structure and to put on your own server TCP/IP server created just with the sockets.
### Technologies Used
Project is created with:
* Python V 3.8
### Project Structure
In the project there are 5 files:
* main.py - main working file
* DownloadManager.py - this file is responsable for downloading all the information from the server with using of threads.
* Parser.py - this file is responsable for parsing the data from .yaml, .xml, .csv, .json formats in the dictionary.
* Server.py - this is where is craeted concurent TCP/IP server.
* PubSub.py - responsable for events handling.
## Laboratory Work Nr 2
### General Info
The scope of the project is to impliment:
*Transport protocl based on UDP protocol*
*Add the session level security to the protocol*
*Impliment Application level protocol*
### Technologies Used
Project is created with:
* Python V 3.8
### Project Structure
Project consist of 4 files:
* server_udp.py - serves the role of the server in the net
* client_udp.py - serves the role of the client in the net
* security_layer.py - security-level based methods are implimented here
* udp_protocol.py - Transport layer functions are implimented here
#### udp_protocol.py
The main idea was to have somethink similar to the simplified TCP/IP pocket. Class Packet consist of dictionary which represent the pocket itself and with function which helps to make pocket and to transform the pocket in bytes for transmission.

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
#### security_layer.py            
 Security level is consisting of diffi heiman key protocol exchange and asymetric cryptography merhod to encrypt the data. After handshake based on diffie heiman, the shared key is used for the encrypting and decrypting messages. 
 The diffie heiman works according to the 2 public keys and for every client and server has their own private key. They mix that all and then they talk with the use of this shared generated key.
    
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
 
