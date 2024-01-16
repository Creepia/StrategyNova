@echo off
rem 检测当前目录下是否有python310文件夹
if exist python310 (
  rem 检测是否有各种包
  .\python310\python.exe -c "import numpy,pandas,streamlit,talib,efinance,st_pages" 2>nul
  rem 如果有任何一个缺少，就安装所有的包
  if errorlevel 1 (
    echo Some packages are missing, installing from requirements.txt
    .\python310\python.exe -m pip install -r requirements.txt
  ) else (
    echo All packages are installed
  )
) else (
  rem 如果没有python310文件夹，就提示用户
  echo python310 folder is not found in the current directory
)
.\python310\Scripts\streamlit.exe run ui_index.py
echo Running ui_index.py ...
pause
