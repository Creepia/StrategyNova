@echo off
rem 检测当前目录下是否有python310文件夹
if exist python310 (
    rem pip安装所有的包
    echo Checking the requirements
    .\python310\python.exe -m pip install -r requirements.txt
) else (
  rem 如果没有python310文件夹，就提示用户
  echo python310 folder is not found in the current directory
)
rem 运行程序
echo Running home.py ...
.\python310\Scripts\streamlit.exe run home.py