@echo off

echo This might take a while...

@REM for playsound module: https://github.com/TaylorSMarks/playsound/issues/145
pip install wheel setuptools pip --upgrade

pip install -r requirements.txt

if not exist ".\screenshots\" mkdir screenshots
if not exist ".\logs\" mkdir logs
if not exist config.ini copy template.ini config.ini
if not exist ".env" (echo EMAIL="" && echo PASSWORD="" && echo SMTP_SERVER="smtp.gmail.com" && echo MIAO_CODE="") > .env