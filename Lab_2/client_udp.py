from security_layer import Security


client_sock = Security('localhost', 8000)
client_sock.connect_to_addr('localhost', 8080)
client_sock.recieve_handshake_client()
