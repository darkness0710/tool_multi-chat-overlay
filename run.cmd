@echo off
rem A venv of its own, deliberately, NOT the project's.
rem
rem TikTokLive drags in protobuf, httpx and a websocket stack; the video
rem pipeline next door runs on numpy, opencv and yt-dlp. Installing this lot
rem on top of that risks a resolver picking a version that breaks the thing
rem this repository is actually for, to run a chat window. Keeping them apart
rem costs a folder.
setlocal
cd /d "%~dp0"

set VENV=.venv
set PY=%VENV%\Scripts\python.exe

if not exist "%PY%" goto :make
"%PY%" -c "import TikTokLive, yt_dlp" 2>nul
if errorlevel 1 goto :install
goto :run

:make
echo Building this tool's own environment (first run, 1-2 minutes)...
where py >nul 2>nul
if errorlevel 1 (python -m venv "%VENV%") else (py -3 -m venv "%VENV%")
if not exist "%PY%" (
  echo Could not create the venv. Python 3 must be on PATH.
  pause
  exit /b 1
)

:install
echo Installing libraries...
"%PY%" -m pip install --disable-pip-version-check -q -U pip
"%PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo.
  echo Install failed. See the messages above.
  pause
  exit /b 1
)

:run
set PYTHONIOENCODING=utf-8
"%PY%" merge_chat.py %*
echo.
pause
