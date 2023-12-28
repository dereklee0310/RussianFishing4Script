pip install -r requirements.txt

@REM for playsound package
@REM reference: https://github.com/TaylorSMarks/playsound/issues/145
pip install wheel setuptools pip --upgrade 
python setup.py