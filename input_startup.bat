@echo off
title Input
waitress-serve --host=0.0.0.0 --port=5000 --threads=6 --call web.input.main:create_app
pause