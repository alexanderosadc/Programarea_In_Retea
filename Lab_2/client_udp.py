from udp_protocol import Socket


client_sock = Socket('localhost', 8000)
client_sock.connect_to_addr('localhost', 8080)
# client_sock.send('BLKJfsafasaf', False)
# client_sock.receive_data()
client_sock.recieve_handshake_client()
