from PubSub import EventChannel
from DownloadManager import DownloadManager

def print_message(x):
    print(x)


# events = EventChannel()
# callback = print_message
downloadManager = DownloadManager(base_url="http://localhost:5000",
                                  register_url="http://localhost:5000/register")
downloadManager.access_root()