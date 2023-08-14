@echo off
cd %~dp0
call "combine-venv\Scripts\activate.bat"
cmd /c "python app.py"
