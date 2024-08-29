from pathlib import Path

import gspread
from gspread import Worksheet
from gspread.utils import Dimension
from typing_extensions import override

from clients.databases.contracts import CVW17Database
from clients.databases.database_client import DatabaseClient
from clients.databases.google_sheets.constants import GOOGLE_SHEETS_KEY_PATH, CVW17_RANGES, GoogleSheetsRanges
from core.constants import ON_DB_INSERT_CALLBACK, MSN_DATA_FILES_PATH
from core.config.config import ConfigSingleton
from core.wrappers import safe_execute
from services.data_handler import DataHandler
import services.Logger as Logger

import numpy as np

from services.file_handler import FileHandler
from services.msn_data.contracts import MsnDataEntry
from services.msn_data.msn_data_handler import MsnDataHandler


class GoogleSheetsClient(DatabaseClient):
    def __init__(self):
        super().__init__()
        self.__google_sheets_api = gspread.service_account(GOOGLE_SHEETS_KEY_PATH)

        self.__config = ConfigSingleton.get_instance()

        self.__spreadsheet = self.__google_sheets_api.open_by_url(self.__config.spreadsheet_url)
        self.__db_sheet = self.__spreadsheet.worksheet("DATABASE")
        self.__entry_sheets = [self.__spreadsheet.worksheet("ENTRY1")]
        self.__misc_sheets = [self.__spreadsheet.worksheet("MISC1")]

        self.__db_snapshot = CVW17Database()

        self.__db_headers: list[str] = []
        self.__fetch_db(self.__get_cell_values())


    @safe_execute
    def __get_cell_values(self) -> dict[GoogleSheetsRanges, list]:
        data = self.__spreadsheet.values_batch_get(ranges=CVW17_RANGES)["valueRanges"]
        return {enum_item: val.get('values', [[]]) for enum_item, val in zip(GoogleSheetsRanges, data)}

    @safe_execute
    def __fetch_db(self, values: dict[GoogleSheetsRanges, list]) -> None:
        if len(self.__db_headers) == 0:
            self.__db_headers = DataHandler.flatten(values[GoogleSheetsRanges.database_headers])

        db = values[GoogleSheetsRanges.database]

        for row in db:
            DataHandler.pad(row, len(self.__db_headers), '')

        db_transposed = np.array(db).T

        lock = db_transposed[self.__db_headers.index('LOCK')][0] == "TRUE"
        if lock:
            return

        fetched_db = CVW17Database()

        fetched_db.date = db_transposed[self.__db_headers.index('DATE')]
        fetched_db.fl_name = db_transposed[self.__db_headers.index('FL NAME')]
        fetched_db.squadron = db_transposed[self.__db_headers.index('SQUADRON')]
        fetched_db.rio_name = db_transposed[self.__db_headers.index('RIO NAME')]
        fetched_db.pilot_name = db_transposed[self.__db_headers.index('PLT NAME')]
        fetched_db.tail_number = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('TAIL NUMBER')], int, None)
        fetched_db.weapon_type = db_transposed[self.__db_headers.index('WEAPON TYPE')]
        fetched_db.weapon = db_transposed[self.__db_headers.index('WEAPON')]
        fetched_db.target = db_transposed[self.__db_headers.index('TARGET')]
        fetched_db.target_angels = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('TARGET ANGELS')], int, None)
        fetched_db.angels = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('ANGELS')], int, None)
        fetched_db.speed = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('SPEED')], float, None)
        fetched_db.range = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('RANGE')], int, None)
        fetched_db.hit = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('HIT')], bool, None)
        fetched_db.destroyed = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('DESTROYED')], bool, None)
        fetched_db.qty = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('QTY')], int, None)
        fetched_db.msn_nr = DataHandler.safe_cast_array(db_transposed[self.__db_headers.index('MSN NR')], int, None)
        fetched_db.msn_name = db_transposed[self.__db_headers.index('MSN NAME')]
        fetched_db.event = db_transposed[self.__db_headers.index('EVENT')]
        fetched_db.notes = db_transposed[self.__db_headers.index('NOTES')]
        fetched_db.size = len(fetched_db.date)

        old_db_size = self.__db_snapshot.size
        self.__db_snapshot = fetched_db

        if fetched_db.size > old_db_size > 0:
            try:
                for func in self.callbacks[ON_DB_INSERT_CALLBACK]:
                    func()
            except Exception as err:
                Logger.warning("failed executing callback func: " + str(err))


    def __update_msn_data_files(self, values: dict[GoogleSheetsRanges, list]) -> None:
        remote_msn_data_files: list[str] = DataHandler.flatten(values[GoogleSheetsRanges.msn_data_files])[:5]

        local_msn_data_paths: list[Path] = FileHandler.sort_files_by_date_created(MSN_DATA_FILES_PATH)[:5]
        local_msn_data_files: list[str] = DataHandler.pad([str(x.with_suffix('')) for x in local_msn_data_paths],
                                                          5, '')

        if remote_msn_data_files == local_msn_data_files:
            return

        files_range: str = GoogleSheetsRanges.msn_data_files.value.split('!')[1]

        # MSN DATA FILES in MISCx sheets
        self.__misc_sheets[0].update(
            range_name= files_range,
            major_dimension=Dimension.cols,
            values=[local_msn_data_files]
        )

        if (local_msn_data_files[0] == remote_msn_data_files[0] or
            values[GoogleSheetsRanges.msn_data_file][0][0] == local_msn_data_files[0]):
            return

        file_range: str = GoogleSheetsRanges.msn_data_file.value.split('!')[1]

        # MSN DATA FILE in ENTRYx sheets
        self.__entry_sheets[0].update(
            range_name= file_range,
            values=[[local_msn_data_files[0]]]
        )


    def __update_entry_id_table(self, values: dict[GoogleSheetsRanges, list], sheet: Worksheet,
                              entries: list[MsnDataEntry]):
        searched_modexes = DataHandler.flatten(values[GoogleSheetsRanges.entry_modexes], True, '')
        msn_modexes = [x.tail_number for x in entries]

        update_values = []
        for modex in searched_modexes:
            # Uncorrelated modexes / not found in search

            if not modex or modex not in msn_modexes:
                update_values.append([])
                continue

            for entry in entries:
                if entry.tail_number == modex and [entry.pilot_name, entry.rio_name] not in update_values:
                    update_values.append([entry.pilot_name, entry.rio_name])

        sheet.update(
            range_name=GoogleSheetsRanges.id_table.get_cell_range(),
            values=update_values,
            major_dimension=Dimension.rows
        )

    def __update_entry_dataview(self, values: dict[GoogleSheetsRanges, list], sheet: Worksheet,
                                entries: list[MsnDataEntry]):
        selected_modexes = DataHandler.flatten(values[GoogleSheetsRanges.entry_modexes], True, '')
        selected_crews = values[GoogleSheetsRanges.id_table]

        modex_to_crew = {modex: crew for modex, crew in zip(selected_modexes, selected_crews) if modex}
        uncorrelated_modexes = selected_modexes
        updated_values = []

        for entry in entries:
            if entry.tail_number in selected_modexes and entry.tail_number:
                weapon_type = 'A/A' if entry.type == 1 else 'A/G'
                row = [entry.pilot_name, int(entry.tail_number), weapon_type, entry.weapon_name, entry.tgt_name,
                       entry.angels_tgt, entry.angels, entry.speed, entry.range, entry.hit, entry.destroyed ]
                updated_values.append(row)
                uncorrelated_modexes.remove(entry.tail_number)

        for modex in uncorrelated_modexes:
            if modex and modex_to_crew.get(modex, []):
                updated_values.append([modex_to_crew[modex][0], int(modex), "N/A", "NONE", "NONE", "", "", "", "", False, False])

        while len(updated_values) < 122:
            updated_values.append(DataHandler.pad([], 11, ''))

        sheet.update(
            range_name=GoogleSheetsRanges.entry_dataview.get_cell_range(),
            values=updated_values,
            major_dimension=Dimension.rows
        )

    def __update_entry_sheet(self, values: dict[GoogleSheetsRanges, list], sheet: Worksheet) -> None:
        msn_data_file_path = Path(MSN_DATA_FILES_PATH.as_posix() + values[GoogleSheetsRanges.msn_data_file][0][0] + ".json")
        entries = MsnDataHandler.load_entries_from_file(msn_data_file_path)

        self.__update_entry_id_table(values, sheet, entries)
        self.__update_entry_dataview(values, sheet, entries)

    @override
    @safe_execute
    def update(self):
        cell_values = self.__get_cell_values()
        if not cell_values:
            return

        self.__update_msn_data_files(cell_values)
        if cell_values[GoogleSheetsRanges.entry_should_update][0][0] == 'TRUE':
            self.__update_entry_sheet(cell_values, self.__entry_sheets[0])
        self.__fetch_db(cell_values)

    @override
    def insert(self, rows: CVW17Database):
        ...

    @override
    def _get_db(self) -> CVW17Database:
        return self.__db_snapshot
