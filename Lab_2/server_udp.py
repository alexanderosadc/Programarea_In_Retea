from security_layer import Security

server_sock = Security('localhost', 8080)
server_sock.recieve_handshake_server()
