import copy
from pprint import pprint

from PubSub import events
import xmltodict
import yaml


class Parser:
    def __init__(self):
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
        list_with_elements = self.merge_dictionaries(list_with_elements)
        events.publish("parsing_finished", list_with_elements)

    def merge_dictionaries(self, list_of_dict):
        for selected_dictionary in list_of_dict:
            list_without_selected_dict = copy.deepcopy(list_of_dict)

            list_without_selected_dict.remove(selected_dictionary)
            # print(len(list_without_selected_dict))
            for compared_element in list_without_selected_dict:
                common_elements_in_dict = (compared_element.items() & selected_dictionary.items())
                for i in range(0, 20):
                    common_elements_in_dict -= {('id', str(i))}

                common_elements_in_dict -= {('gender', 'Female')} - {('gender', 'Male')} \
                                          - {('organization', 'Yotz')} - {('card_balance', None)}
                if common_elements_in_dict:
                    selected_dictionary.update(compared_element)

        # self.delete_copies(list_of_dict)
        list_of_dict = self.add_full_name(list_of_dict)
        list_of_dict = self.remove_duplicates(list_of_dict)
        return list_of_dict

    def add_full_name(self, list_of_dict):
        for selected_element in list_of_dict:
            if 'full_name' not in selected_element and \
                    'first_name' in selected_element \
                    and 'last_name' in selected_element:
                selected_element['full_name'] = selected_element['first_name'] + ' ' + \
                                                selected_element['last_name']
        return list_of_dict


    def remove_duplicates(self, list_of_dict):
        result_list = []
        for selected_dict in list_of_dict:
            if selected_dict not in result_list:
                result_list.append(selected_dict)
        return result_list

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
