from web.input.config.config import InteractiveMapConfigSingleton

_map_config = InteractiveMapConfigSingleton.get_instance()

class Maps:
    @staticmethod
    def get_current_id():
        current_map = _map_config.current_map
        id_ = 0
        for i, map_ in enumerate(_map_config.maps):
            if current_map in map_:
                id_ = i
                break
        return id_

    @classmethod
    def get_ref_dms(cls):
        return _map_config.map_reference[cls.get_current_id()].replace('Â°', '°')
