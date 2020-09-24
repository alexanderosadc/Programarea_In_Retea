from PubSub import events


class Parser:
    def __init__(self):
        callback = self.check_type_of_file
        events.subscribe('download_ended', callback)

    def check_type_of_file(self, callback):
        print(callback)
