from clients.databases.contracts import CVW17Database
from core.constants import MSN_DATA_FILES_PATH
from services.file_handler import FileHandler
from services.msn_data.contracts import MsnDataEntry
from services.msn_data.msn_data_handler import MsnDataHandler

"""
    MsnDataMonitor monitors the latest msn data file (in ../MissionData/ by default) for changes and stores all the
    data that should be inserted into the db while in auto mode.

"""

class MsnDataMonitor:
    def __init__(self):
        self.active_file: str = ""
        self.msn_nr: int = 40000 # This will be 40000 + the files in MSN_DATA_FILES dir. 40001 is Auto mode, first file
        self.to_insert: CVW17Database = CVW17Database()
        self.current_msn_data: list[MsnDataEntry] = []
        self.old_msn_data: list[MsnDataEntry] = []

    def __get_latest_file(self):
        return FileHandler.sort_files_by_date_created(MSN_DATA_FILES_PATH)[0]

    def __update_msn_nr(self):
        self.msn_nr = 40000 + len(FileHandler.get_files_from_directory(MSN_DATA_FILES_PATH))

    def __update_active_file(self, latest_file):
        if self.active_file != latest_file:
            self.active_file = latest_file
            self.current_msn_data = []

    def __update_msn_data(self, latest_file):
        latest_file_data = FileHandler.load_json(MSN_DATA_FILES_PATH / latest_file)
        if self.current_msn_data != latest_file_data:
            self.old_msn_data = self.current_msn_data
            self.current_msn_data = MsnDataHandler.load_entries_from_dict(latest_file_data)

    def __update_to_insert(self):
        new_data = MsnDataHandler.get_difference_between_entries(self.old_msn_data, self.current_msn_data)
        MsnDataHandler.add_entries_to_db(new_data, self.to_insert, self.msn_nr)

    def update(self):
        # read the file
        # compare to local file copy from last update()
        # add any changes to to_insert
        latest_file = self.__get_latest_file()

        self.__update_msn_nr()
        self.__update_active_file(latest_file)
        self.__update_msn_data(latest_file)
        self.__update_to_insert()

        print(self.to_insert)
