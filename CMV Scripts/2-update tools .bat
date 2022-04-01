call C:\PythonSV\__install__\3.6_64bit\associate_python_files_with_python_launcher.bat
python C:\PythonSV\__install__\3.6_64bit\set_default_python_to_36.py
python C:\PythonSV\__install__\install_update_tools.py
python C:\PythonSV\__install__\installpath.py

IF EXIST C:\PythonSV\icelakex\update_tools.py python C:\PythonSV\icelakex\update_tools.py

IF EXIST C:\PythonSV\icelakex\update_tools.py python C:\PythonSV\sapphirerapids\update_tools.py

echo running update_tools for pvc
python C:\PythonSV\pontevecchio\update_tools.py