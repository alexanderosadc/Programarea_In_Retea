class EventChannel(object):
    def __init__(self):
        self.subscribers = {}

    def create_event(self, event):
        self.subscribers[event] = []

    def print_subscribe_message(self, callback):
        print("Subscribed: ")

    def subscribe(self, event, callback):
        if not callable(callback):
            raise ValueError("callback must be callable")

        if event is None or event == "":
            raise ValueError("Event cant be empty")

        if event not in self.subscribers.keys():
            raise ValueError("Event does not exist")
        else:
            self.subscribers[event].append(callback)

    def publish(self, event, args=None):
        if event in self.subscribers.keys():
            for callback in self.subscribers[event]:
                if args is not None:
                    callback(args)
                else:
                    callback()