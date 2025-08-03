import re
import zipfile
from pathlib import Path

from services.file_handler import FileHandler
from web.input.config.config import WebConfigSingleton

from slpp import slpp as lua

config = WebConfigSingleton.get_instance()

class Mission:
    @classmethod
    def get_path(cls) -> Path | None:
        miz_path = None
        for msn in FileHandler.sort_files_by_date_modified(config.missions_path):
            msn_sanitized = str(msn.name).strip().lower()
            if not msn_sanitized.endswith('.miz'):
                continue

            if not msn_sanitized.startswith(config.deployment_msn_prefix.strip().lower()):
                continue

            miz_path = msn
            break

        return miz_path

    @classmethod
    def __get_msn_content(cls) -> str:
        try:
            with zipfile.ZipFile(cls.get_path(), 'r') as miz_archive:
                return miz_archive.read('mission').decode('utf-8')
        except Exception as e:
            print(e)
            return ""

    @classmethod
    def __get_unit_data(cls, mission_content, unit_type) -> list:
        try:
            unit_pattern = re.compile(re.escape(unit_type))
            units = []

            for match in unit_pattern.finditer(mission_content):
                unit_start = match.start()

                # Find the opening brace before the unit_type
                unit0_start = mission_content.rfind('{', 0, unit_start)
                if unit0_start == -1:
                    continue

                pos = unit0_start + 1
                brace_open = 1
                brace_close = 0

                # Find the matching closing brace
                while pos < len(mission_content) and brace_open != brace_close:
                    if mission_content[pos] == '{':
                        brace_open += 1
                    elif mission_content[pos] == '}':
                        brace_close += 1
                    pos += 1

                # Extract the unit data
                unit = mission_content[unit0_start:pos]
                unit_table = lua.decode(unit)

                # Add the unit values to our list
                units.append(unit_table)

            return units

        except Exception as e:
            print(f"Error parsing mission file: {e}")
            return []

    @classmethod
    def __get_miz_ship_data(cls, mission_content, cv_type='CVN_73') -> dict:
        try:
            cv_start = mission_content.find(cv_type)
            if cv_start == -1:
                return {}

            unit0_start = mission_content.rfind('{', 0, cv_start)
            if unit0_start == -1:
                return {}

            units_start = mission_content.rfind('{', 0, unit0_start-1)
            if units_start == -1:
                return {}

            pos = units_start + 1

            brace_open = 1
            brace_close = 0

            while brace_open != brace_close:
                if mission_content[pos] == '{':
                    brace_open += 1
                elif mission_content[pos] == '}':
                    brace_close += 1
                pos += 1

            units = mission_content[units_start:pos]
            units_table = lua.decode(units)

            return units_table.values()

        except Exception as e:
            print(f"Error parsing mission file: {e}")
            return {}

    @classmethod
    def get_miz_tanker_data(cls) -> dict:
        try:
            mission_content = cls.__get_msn_content()
            name_pattern = r'\["name"\]\s*=\s*"(TANKER-TRACK-(?![\d\s]*")[^"]+)"'
            tanker_mentions = set(re.findall(name_pattern, mission_content))

            res = {}

            for tanker in tanker_mentions:
                tanker_c = mission_content.find(tanker)

                bracket_close = mission_content.find('}', tanker_c)
                eol = mission_content.find('\n', bracket_close)
                if '[1]' not in mission_content[bracket_close:eol]:
                    continue

                x1_pos = mission_content.find('["x"] = ', eol)+len('["x"] = ')
                y1_pos = mission_content.find('["y"] = ', eol)+len('["y"] = ')
                x1_comma = mission_content.find(',', x1_pos)
                y1_comma = mission_content.find(',', y1_pos)

                bracket_close = mission_content.find('}', x1_comma)
                eol = mission_content.find('\n', bracket_close)
                if '[2]' not in mission_content[bracket_close:eol]:
                    continue

                x2_pos = mission_content.find('["x"] = ', eol)+len('["x"] = ')
                y2_pos = mission_content.find('["y"] = ', eol)+len('["y"] = ')
                x2_comma = mission_content.find(',', x2_pos)
                y2_comma = mission_content.find(',', y2_pos)


                x1 = float(mission_content[x1_pos:x1_comma])
                y1 = float(mission_content[y1_pos:y1_comma])

                x2 = float(mission_content[x2_pos:x2_comma])
                y2 = float(mission_content[y2_pos:y2_comma])

                res[tanker] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

            return res

        except Exception as e:
            print(f"Error parsing mission file: {e}")
            return {}

    @classmethod
    def get_miz_nav_points(cls) -> list[dict]:
        try:
            mission_content = cls.__get_msn_content()

            coalition_start = mission_content.find('["coalition"]')
            if coalition_start == -1:
                return []

            red_start = mission_content.find('["red"]', coalition_start)
            if red_start == -1:
                return []

            nav_start = mission_content.find('["nav_points"]', red_start)
            if nav_start == -1:
                return []

            equals_pos = mission_content.find('=', nav_start)
            if equals_pos == -1:
                return []

            brace_start = mission_content.find('{', equals_pos)
            if brace_start == -1:
                return []

            # Count braces to find the matching closing brace
            pos = brace_start + 1

            brace_open = 1
            brace_close = 0

            while brace_open != brace_close:
                if mission_content[pos] == '{':
                    brace_open += 1
                elif mission_content[pos] == '}':
                    brace_close += 1
                pos += 1

            # Extract the red coalition content
            nav_content = mission_content[brace_start:pos]
            nav_points = lua.decode(nav_content)

            dmpi_pattern = re.compile(r'^[^-]+-[^-]+-\d{5}-\d{2}$')
            result = [x for x in nav_points.values()
                      if dmpi_pattern.match(x.get('callsignStr', ''))]
            return result
        except Exception as e:
            print(f"Error parsing mission file: {e}")
            return []

    @classmethod
    def get_msn_unit(cls, unit_type):
        msn_content = cls.__get_msn_content()
        return cls.__get_unit_data(msn_content, unit_type)

    @classmethod
    def get_msn_units(cls):
        msn_content = cls.__get_msn_content()

        units = []
        for cv in ['CVN_73', 'CVN_75', 'hms_invincible', 'LHA_Tarawa']:
            ship_data = cls.__get_miz_ship_data(msn_content, cv)
            for ship in ship_data:
                units.append(ship)

        units.extend(cls.__get_unit_data(msn_content, 'Patriot str'))
        units.extend(cls.__get_unit_data(msn_content, 'KC135MPRS'))

        return units
