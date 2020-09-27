from PubSub import events
import json
import xmltodict
import yaml
import csv
from pprint import pprint


class Parser:
    def __init__(self):
        self.json = []
        callback = self.check_type_of_file
        events.subscribe('download_ended', callback)

    def check_type_of_file(self, callback):
        list_with_elements = []
        list_with_dict = []
        while not callback.empty():
            item = callback.get()

            if item[-1] == 'application/x-yaml':
                pass
                # list_with_elements.append(self.parse_yaml(item[0]))
            elif item[-1] == 'json':
                list_with_elements.extend(self.parse_json(item[0]))
            elif item[-1] == 'application/xml':
                # list_with_elements.extend(self.parse_xml(item[0]))
                pass
            elif item[-1] == 'text/csv':
                pass
                # list_with_elements.append(self.parse_csv(item[0]))

            callback.task_done()
            # pprint(list_with_elements)
        # for item in jsons_from_queue:
        #     print(item)

    def parse_yaml(self, data):
        data_dict = yaml.safe_load(data)
        return data_dict

    def parse_csv(self, data):
        data_dict = csv.DictReader(data)
        list_of_data = list(data_dict)
        return dict(enumerate(list_of_data))

    def parse_xml(self, data):
        data = xmltodict.parse(data)['dataset']['record']
        list_of_dict = []
        for item in data:
            list_of_dict.append(dict(item))
        return list_of_dict

    def parse_json(self, data):
        elements_list = []
        final_list = []
        data = data[:-1]
        data = data.replace('[', "")
        data = data.replace(']', "")
        elements_list = data.split('\n')
        for item in elements_list:
            item = json.dumps(data)
            # print(item)
            final_list.append(json.loads(item))
            # print(item)
        pprint(final_list)
        return data
