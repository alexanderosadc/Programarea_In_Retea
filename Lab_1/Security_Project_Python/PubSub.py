class EventChannel(object):
    def __init__(self):
        self.subscribers = {}

    def create_event(self, event):
        self.subscribers[event] = [self.print_subscribe_message]

    def print_subscribe_message(self, callback):
        print("Event Raised")

    def subscribe(self, event, callback):
        if not callable(callback):
            raise ValueError("callback must be callable")

        if event is None or event == "":
            raise ValueError("Event cant be empty")

        if event not in self.subscribers.keys():
            raise ValueError("Event does not exist")
            # self.subscribers[event] = [callback]
        else:
            self.subscribers[event].append(callback)

    def publish(self, event, args=None):
        if event in self.subscribers.keys():
            for callback in self.subscribers[event]:
                if args is not None:
                    callback(args)
                else:
                    callback()


events = EventChannel()
events.create_event("download_ended")
