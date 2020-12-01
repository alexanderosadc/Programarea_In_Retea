from udp_protocol import Socket

server_sock = Socket('localhost', 8080)
server_sock.recieve_handshake_server()
# server_sock.receive_data()
