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

        while not callback.empty():
            item = callback.get()

            if item[-1] == 'application/x-yaml':
                list_with_elements.extend(self.parse_yaml(item[0]))
            elif item[-1] == 'json':
                list_with_elements.extend(self.parse_json(item[0]))
            elif item[-1] == 'application/xml':
                list_with_elements.extend(self.parse_xml(item[0]))
            elif item[-1] == 'text/csv':
                list_with_elements.extend(self.parse_csv(item[0]))
            callback.task_done()
        # pprint(list_with_elements)
        self.merge_dictionaries(list_with_elements)

    def merge_dictionaries(self, list_of_dict):
        keys_to_verify = ['email', 'first_name', 'ip_address', 'last_name',
                          'bitcoin_address', 'card_number', 'username',
                          'employee_id', 'full_name']
        ids_to_merge = []

        for i in range(0, len(list_of_dict)):
            for j in range(i + 1, len(list_of_dict)):
                common_values = list_of_dict[i].items() & list_of_dict[j].items()
                is_value_accepted = True
                for element in common_values:
                    if element[0] not in keys_to_verify:
                        is_value_accepted = False

                if is_value_accepted:
                    ids_to_merge.append(i)
                    ids_to_merge.append(j)

                    # if list_of_dict[i][key] == list_of_dict[j][key]:




                # pprint(list_of_dict[i])
                # pprint(list_of_dict[j])

    def parse_yaml(self, data):
        data_dict = yaml.safe_load(data)
        return data_dict

    def parse_csv(self, data):
        final_list_of_dictionaries = []
        table_of_persons = data.split('\n')
        headers = []
        for i in range(0, len(table_of_persons)):
            if i == 0:
                headers = table_of_persons[i].split(',')
            else:
                dictionary = {}
                elements = table_of_persons[i].split(',')
                for i in range(0, len(elements)):
                    if elements[i] != '':
                        dictionary[headers[i]] = elements[i]
                if dictionary:
                    final_list_of_dictionaries.append(dictionary)

        # list_of_data = list(data_dict)
        return final_list_of_dictionaries

    def parse_xml(self, data):
        data = xmltodict.parse(data)['dataset']['record']
        list_of_dict = []
        for item in data:
            list_of_dict.append(dict(item))
        return list_of_dict

    def parse_json(self, data):
        final_list = []
        data = data[:-1]
        data = data.replace('[', '')
        data = data.replace(']', '')
        data = data.replace('{', '')
        data = data.replace('}', '')
        elements_list = data.split('\n')
        for item in elements_list:
            dictionary_of_person = {}
            elements = item.split(',')
            for element in elements:
                if element != "":
                    element = element.replace('"', '')
                    left_right_sides = element.split(':')
                    dictionary_of_person[left_right_sides[0]] = left_right_sides[1]
            final_list.append(dictionary_of_person)

        return final_list