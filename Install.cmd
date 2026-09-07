@echo off
rem Build the environment this tool runs in, and say whether it worked.
rem
rem run.cmd does this by itself the first time, so this file is for the two
rem cases that one cannot serve: installing ahead of time, and repairing.
rem
rem   Install.cmd            build it, or leave it alone if it is already there
rem   Install.cmd -u         update the libraries to their latest
rem   Install.cmd -f         throw the environment away and build it again
setlocal
cd /d "%~dp0"

set VENV=.venv
set PY=%VENV%\Scripts\python.exe

if /i "%~1"=="-f" goto :fresh
if /i "%~1"=="-u" goto :upgrade
if exist "%PY%" goto :install
goto :make

:fresh
echo Removing the old environment...
if exist "%VENV%" rmdir /s /q "%VENV%"
goto :make

:make
echo.
echo [1/3] Find Python -- installs one if this machine has none, no Administrator needed
rem get_python.ps1 prints one path and nothing else; everything it has to say
rem goes to the console instead, so this reads the path cleanly.
set BASEPY=
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0get_python.ps1"`) do set BASEPY=%%P
if not defined BASEPY (
  echo.
  echo   No usable Python -- see the messages above.
  goto :fail
)
echo   using: %BASEPY%
echo   building its own environment in %CD%\%VENV%
"%BASEPY%" -m venv "%VENV%"
if not exist "%PY%" (
  echo.
  echo   Creating the venv with %BASEPY% failed
  goto :fail
)

rem Python moi du: TikTokLive, TikTokLiveProto, EulerApiSdk va yt-dlp deu
rem khai bao Requires-Python >=3.10. Kiem o day de bao dung benh, thay vi de
rem pip bao mot loi giai phu thuoc kho hieu o buoc sau.
"%PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo.
  echo   This machine's Python is too old:
  "%PY%" -c "import sys; print('     ', sys.version.split()[0])"
  echo   3.10 or newer is needed. Get one from python.org, then run:  Install.cmd -f
  goto :fail
)

rem MAX_PATH. Windows 10 and 11 still ship with long paths disabled, and
rem EulerApiSdk is a generated client with filenames like
rem record_string_is_live_boolean_room_id_string_or_null_additional_property.py
rem -- measured, the deepest path this install creates is 156 characters below
rem the folder, so anything past 103 characters here cannot fit in 260. Seen
rem for real: pip got most of the way in and died with "No such file or
rem directory" on that one file.
"%PY%" -c "import os,sys; n=len(os.path.abspath('.')); sys.exit(0 if n<=100 else 1)"
if errorlevel 1 (
  echo.
  echo   The path to this folder is too long for Windows:
  "%PY%" -c "import os; p=os.path.abspath('.'); print('     ', len(p), 'characters:', p)"
  echo   100 characters at most. Quickest fix: move the whole chat_merge
  echo   folder somewhere shorter, say  C:\chat_merge  and run Install.cmd again
  echo.
  echo   The other way ^(needs Administrator^): turn on Windows long paths,
  echo   see https://pip.pypa.io/warnings/enable-long-paths
  goto :fail
)
goto :install

:upgrade
if not exist "%PY%" goto :make
echo.
echo [1/3] Environment is already there; updating the libraries
set UP=-U

:install
echo.
echo [2/3] Install libraries %UP%
"%PY%" -m pip install --disable-pip-version-check -q -U pip
"%PY%" -m pip install --disable-pip-version-check %UP% -r requirements.txt
if errorlevel 1 (
  echo.
  echo   pip reported an error. "Access is denied" is usually a virus scanner
  echo   holding a file open as pip writes it -- run Install.cmd once more.
  goto :fail
)

:check
echo.
echo [3/3] Check
"%PY%" -c "import TikTokLive, yt_dlp, pytchat, chat_downloader; print('   libraries: ok')"
if errorlevel 1 (
  echo   Libraries are missing. Try:  Install.cmd -f
  goto :fail
)
"%PY%" -m pip check
if errorlevel 1 (
  echo   pip check reports mismatched dependencies. Try:  Install.cmd -f
  goto :fail
)

echo.
echo Done. What to run next:
echo    web.cmd     the OBS overlay, at http://127.0.0.1:8770/
echo    run.cmd     the console window only
echo.
pause
exit /b 0

:fail
echo.
echo Not installed yet. See documents\install.md for more.
echo.
pause
exit /b 1
