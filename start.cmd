@echo off
cd %~dp0
call "venv\Scripts\activate.bat"
cmd /c "python app.py"
