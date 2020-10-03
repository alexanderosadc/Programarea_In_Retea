import socket
from PubSub import events

class Server:

    def __init__(self):
        self.HOST = '0.0.0.0'
        self.PORT = 65432
        callback = self.start_server
        events.subscribe('parsing_finished', callback)

    def start_server(self, list_with_dict):
        print("SERVER STARTED")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
            sc.bind((self.HOST, self.PORT))
            sc.listen()
            conn, addr = sc.accept()
            try:
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
            except Exception:
                pass
            finally:
                conn.close()
                sc.close()