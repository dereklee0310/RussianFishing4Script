@echo off

python -m nuitka ^
  main.py ^
  --windows-icon-from-ico=static/readme/main.ico ^
  --output-dir=dist ^
  --standalone ^
  --onefile ^
  --mingw64 ^
  --include-data-dir=static=static

tar.exe -a -c -f dist/rf4s.zip ^
  LICENSE ^
  -C dist main.exe ^
  -C ../rf4s/config config.yaml