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
