from PubSub import events
from Parser import Parser
from Server import Server
from DownloadManager import DownloadManager


def print_message(x):
    print(x)


downloadManager = DownloadManager(base_url="http://localhost:5000",
                                  register_url="http://localhost:5000/register")
parserManager = Parser()
server = Server()
downloadManager.access_root()

