from PubSub import events
from Parser import Parser
from DownloadManager import DownloadManager


def print_message(x):
    print(x)


downloadManager = DownloadManager(base_url="http://localhost:5000",
                                  register_url="http://localhost:5000/register")
parserManager = Parser()
downloadManager.access_root()
