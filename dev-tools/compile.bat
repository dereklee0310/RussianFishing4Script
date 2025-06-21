python -m nuitka tools\main.py --windows-icon-from-ico=./static/readme/main.ico --output-dir=dist --standalone --onefile --mingw64 --include-data-dir=static=static
if not exist dist mkdir dist
if not exist dist\screenshots mkdir dist\screenshots
if not exist dist\logs mkdir dist\logs
tar.exe -a -c -f dist\rf4s.zip LICENSE config.yaml -C dist main.exe screenshots logs