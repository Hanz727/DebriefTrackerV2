from clients.databases.google_sheets.contracts import CVW17Database

"""
    MsnDataMonitor monitors the latest msn data file (in ../MissionData/ by default) for changes and stores all the
    data that should be inserted into the db while in auto mode.

"""

class MsnDataMonitor:
    def __init__(self):
        self.active_file: str = ""
        self.to_insert: CVW17Database = CVW17Database()
