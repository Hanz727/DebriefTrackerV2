import math

import numpy as np
class DataHandler:
    @classmethod
    def flatten(cls, nested_list: list, include_empty=False, empty_element='') -> list:
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(cls.flatten(item))
                if len(item) == 0 and include_empty:
                    flat_list.append(empty_element)
            else:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def get_hundreth(num: int) -> int:
        return int(math.floor(num / 100) * 100)

    @staticmethod
    def pad(list_: list, length: int, padding_token='') -> list:
        while len(list_) < length:
            list_.append(padding_token)
        return list_

    @staticmethod
    def safe_cast_array(array: np.array, type_: type, default_value) -> np.array:
        if type(default_value) != type_ and default_value is not None:
            raise Exception(f"safe_cast_array has been provided with mismatching types: {type_}, {type(default_value)}")

        new_list = []
        for element in array:
            try:
                to_append = element
                if element == 'TRUE':
                    to_append = True
                if element == 'FALSE':
                    to_append = False

                if type_ == float:
                    to_append = str(to_append).replace(",", ".")

                new_list.append(type_(to_append))
            except:
                new_list.append(default_value)

        return np.array(new_list)