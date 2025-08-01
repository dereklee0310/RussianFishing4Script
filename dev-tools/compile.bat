@echo off

python -m nuitka ^
  main.py ^
  --windows-icon-from-ico=static/readme/main.ico ^
  --output-dir=dist ^
  --standalone ^
  --onefile ^
  --mingw64 ^
  --enable-plugin=tk-inter ^
  --include-data-dir=static=static ^
  --include-data-files=rf4s/config/config.yaml=rf4s/config/config.yaml

tar.exe -a -c -f dist/rf4s.zip ^
  LICENSE ^
  -C dist main.exe