import concurrent
import socket
from pprint import pprint
from concurrent import futures

from PubSub import events

class Server:

    def __init__(self):
        self.list_with_dict = []
        self.HOST = '0.0.0.0'
        self.PORT = 65432
        callback = self.start_server
        events.subscribe('parsing_finished', callback)

    def select_data(self, column, regex=None):
        str_to_send = ''
        for element in self.list_with_dict:
            if column in element.keys():
                str_to_send += element[column] + ',\n'
                # data_to_send.append(element[column])
        return str_to_send

    def connection_with_client(self, conn, addr):
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if data:
                data = data.decode("utf-8")
                list_with_response_data = data.split(' ')
                if list_with_response_data[0] == 'SelectColumn' and \
                        len(list_with_response_data) == 2:
                    print("ColumnSelected")
                    data_to_send = self.select_data(list_with_response_data[1].strip())
                    conn.sendall(data_to_send.encode("utf-8"))
                else:
                    continue
            else:
                conn.sendall(data)
                conn.close()


    def start_server(self, list_with_dict):
        print("SERVER STARTED")
        self.list_with_dict = list_with_dict
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
            sc.bind((self.HOST, self.PORT))
            sc.listen()

            while True:
                conn, addr = sc.accept()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(self.connection_with_client, )