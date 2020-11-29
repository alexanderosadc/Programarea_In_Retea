from udp_protocol import Socket

server_sock = Socket('localhost', 8080)
server_sock.receive()
