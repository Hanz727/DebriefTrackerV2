
class DataHandler:
    @classmethod
    def flatten(cls, nested_list: list) -> list:
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(cls.flatten(item))
            else:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def pad(list_: list, length: int, padding_token='') -> list:
        while len(list_) < length:
            list_.append(padding_token)
        return list_
