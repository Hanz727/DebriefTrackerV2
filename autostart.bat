@echo off
color a
Title "DebriefTracker Discord Bot"

cd MissionData
if exist "AUTOFILLER.json" del "AUTOFILLER.json"
echo [] > "AUTOFILLER.json"
cd ../DebriefTracker
python main.py
pause