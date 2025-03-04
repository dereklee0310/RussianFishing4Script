@echo off

echo This might take a while...

@REM for playsound module: https://github.com/TaylorSMarks/playsound/issues/145
python -m pip install wheel setuptools pip --upgrade
python -m pip install -r requirements.txt

if not exist ".\screenshots" mkdir screenshots
if not exist ".\logs" mkdir logs
if not exist ".\config.yaml" copy ".\rf4s\config\config.yaml" ".\config.yaml"