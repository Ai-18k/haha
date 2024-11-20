@echo off
cd /d %~dp0
call activate spiders
python user_manage.py
pause