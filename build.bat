@echo off
chcp 65001 >nul
rem Сборка dist\wrap_deck_names.ankiaddon для загрузки на AnkiWeb
cd /d "%~dp0"
py -3.12 build.py
pause
