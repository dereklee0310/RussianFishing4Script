@echo off
setlocal

set "ALL_ARGS="

echo Starting
cd src

choice /m "show help?" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  python app.py -h
  pause
)

choice /m "craft items?" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set /p tocraft=Enter Limit of Items to craft: 

  python craft.py
  pause
)

choice /m "switch the gear ratio after the retrieval timed out" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -g"
)


choice /m "shutdown computer after terminated without user interruption" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -s"
)


choice /m "lift the tackle constantly while pulling a fish" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -l"
)


choice /m "change friction brake automatically" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -f"
)


choice /m "recast the spod rod automatically" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -o"
)


choice /m "change current lure with a random one automatically" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -L"
)


choice /m "move mouse randomly before casting the rod" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -x"
)


choice /m "pause the script after catchig a fish regularly" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -X"
)


choice /m "Use rainbow line meter for retrieval detection" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -R"
)


choice /m "harvest baits before casting, support mode: bottom, spin, and float" /c yn
if errorlevel 2 (
  echo "ok"
) else (
  set "ALL_ARGS=%ALL_ARGS% -H"
)


set /p fishnet=Enter current Net Value: 

python app.py -n %fishnet% %ALL_ARGS%
endlocal
pause