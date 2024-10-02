from datetime import datetime

from clients.databases.contracts import CVW17DatabaseRow
from core.constants import MODEX_TO_SQUADRON, Squadrons
from services.data_handler import DataHandler

class InputDataHandler:
    @staticmethod
    def get_row(entries: dict, row_id):
        return CVW17DatabaseRow(datetime.now(),
                                entries.get('FL_NAME', '') or None,
                                MODEX_TO_SQUADRON.get(DataHandler.get_hundreth(int(entries.get(f'tail_number_{row_id}', -100))), Squadrons.NONE)
                                .value or None, # noqa the .value returns str
                                entries.get(f'rio_name_{row_id}', '') or None,
                                entries.get(f'plt_name_{row_id}', None) or None,
                                entries.get(f'tail_number_{row_id}', None) or None,
                                entries.get(f'weapon_type_{row_id}', 'N/A').upper() or None,
                                entries.get(f'weapon_{row_id}', None) or None,
                                entries.get(f'target_{row_id}', None) or None,
                                entries.get(f'target_angels_{row_id}', None) or None,
                                entries.get(f'angels_{row_id}', None) or None,
                                entries.get(f'speed_{row_id}', None) or None,
                                entries.get(f'range_{row_id}', None) or None,
                                entries.get(f'hit_{row_id}', False) is not False,
                                entries.get(f'destroyed_{row_id}', False) is not False,
                                1 if entries.get(f'weapon_type_{row_id}', 'N/A').upper() in ['A/A', 'A/G'] else 0, # QTY
                                entries.get('MSN_NR', None) or None,
                                entries.get('MSN_NAME', None) or None,
                                entries.get('EVENT', "").upper() or None,
                                entries.get('NOTES', None) or None)

    @staticmethod
    def validate_row(row):
        if None in [row.pilot_name, row.fl_name, row.msn_name, row.msn_nr, row.event, row.tail_number, row.hit,
                    row.destroyed, row.weapon_type, row.squadron]:
            return False
        if row.weapon_type not in ['A/A', 'A/G', 'N/A']:
            return False

        return True
