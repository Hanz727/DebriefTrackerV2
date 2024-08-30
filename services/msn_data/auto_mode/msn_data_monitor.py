from clients.databases.contracts import CVW17Database
from clients.databases.database_client import DatabaseClient
from core.constants import MSN_DATA_FILES_PATH
from core.wrappers import safe_execute
from services.file_handler import FileHandler
from services.msn_data.contracts import MsnDataEntry
from services.msn_data.msn_data_handler import MsnDataHandler


class MsnDataMonitor:
    def __init__(self):
        self.__active_file: str = ""
        self.__msn_nr: int = 40000  # This will be 40000 + the files in MSN_DATA_FILES dir. 40001 is Auto mode, first file

        self.__to_insert: CVW17Database = CVW17Database()

        self.__current_msn_data: list[MsnDataEntry] = []
        self.__old_msn_data: list[MsnDataEntry] = []

    def __get_latest_file(self):
        return FileHandler.sort_files_by_date_created(MSN_DATA_FILES_PATH)[0]

    def __update_msn_nr(self):
        self.__msn_nr = 40000 + len(FileHandler.get_files_from_directory(MSN_DATA_FILES_PATH))

    def __update_active_file(self, latest_file):
        if self.__active_file != latest_file:
            self.__active_file = latest_file
            self.__current_msn_data = []
            self.__old_msn_data = []

    def __update_msn_data(self, latest_file):
        latest_file_data = FileHandler.load_json(MSN_DATA_FILES_PATH / latest_file)

        self.__old_msn_data = self.__current_msn_data
        if len(self.__current_msn_data) < len(latest_file_data):
            self.__current_msn_data = MsnDataHandler.validate_entries(
                MsnDataHandler.load_entries_from_dict(latest_file_data)
            )

    def __update_to_insert(self):
        new_data = MsnDataHandler.get_difference_between_entries(self.__old_msn_data, self.__current_msn_data)
        MsnDataHandler.add_entries_to_db(new_data, self.__to_insert, self.__msn_nr)

    def insert_data_into(self, db_client: DatabaseClient):
        if self.__to_insert.size > 0:
            db_client.insert(self.__to_insert)
            self.__to_insert = CVW17Database()

    @safe_execute
    def update(self):
        latest_file = self.__get_latest_file()

        self.__update_msn_nr()
        self.__update_active_file(latest_file)
        self.__update_msn_data(latest_file)
        self.__update_to_insert()