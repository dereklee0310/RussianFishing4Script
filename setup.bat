pip install -r requirements.txt

@REM for playsound package
@REM reference: https://github.com/TaylorSMarks/playsound/issues/145
pip install wheel setuptools pip --upgrade
if not exist ".\screenshots\" mkdir screenshots
if not exist ".env" (echo GMAIL="" && echo APP_PASSWORD="") > .env
python setup.py