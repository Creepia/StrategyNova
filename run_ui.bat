@echo off
if exist python310 (
    echo Checking the requirements
    .\python310\python.exe -m pip install -r requirements.txt
) else (
  echo python310 folder is not found in the current directory
)
echo Running home.py ...
.\python310\Scripts\streamlit.exe run home.py