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
echo Xoa moi truong cu...
if exist "%VENV%" rmdir /s /q "%VENV%"
goto :make

:make
echo.
echo [1/3] Tim Python -- may chua co thi tu cai, khong can Administrator
rem get_python.ps1 prints one path and nothing else; everything it has to say
rem goes to the console instead, so this reads the path cleanly.
set BASEPY=
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0get_python.ps1"`) do set BASEPY=%%P
if not defined BASEPY (
  echo.
  echo   Khong co Python de dung -- xem thong bao o tren.
  goto :fail
)
echo   dung: %BASEPY%
echo   tao moi truong rieng trong %CD%\%VENV%
"%BASEPY%" -m venv "%VENV%"
if not exist "%PY%" (
  echo.
  echo   Tao venv that bai voi %BASEPY%
  goto :fail
)

rem Python moi du: TikTokLive, TikTokLiveProto, EulerApiSdk va yt-dlp deu
rem khai bao Requires-Python >=3.10. Kiem o day de bao dung benh, thay vi de
rem pip bao mot loi giai phu thuoc kho hieu o buoc sau.
"%PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo.
  echo   Python cua may nay qua cu:
  "%PY%" -c "import sys; print('     ', sys.version.split()[0])"
  echo   Can 3.10 tro len. Tai ban moi o python.org roi chay:  Install.cmd -f
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
  echo   Duong dan thu muc nay qua dai cho Windows:
  "%PY%" -c "import os; p=os.path.abspath('.'); print('     ', len(p), 'ky tu:', p)"
  echo   Toi da 100 ky tu. Cach nhanh nhat: chuyen ca thu muc chat_merge sang
  echo   cho ngan hon, vi du  C:\chat_merge  roi chay lai Install.cmd
  echo.
  echo   Cach khac ^(can quyen Administrator^): bat Long Path cua Windows,
  echo   xem https://pip.pypa.io/warnings/enable-long-paths
  goto :fail
)
goto :install

:upgrade
if not exist "%PY%" goto :make
echo.
echo [1/3] Moi truong da co, se cap nhat thu vien len ban moi nhat
set UP=-U

:install
echo.
echo [2/3] Cai thu vien %UP%
"%PY%" -m pip install --disable-pip-version-check -q -U pip
"%PY%" -m pip install --disable-pip-version-check %UP% -r requirements.txt
if errorlevel 1 (
  echo.
  echo   pip bao loi. Neu la "Access is denied" thi thuong la trinh quet virus
  echo   giu file ngay luc pip ghi -- chay lai Install.cmd mot lan nua.
  goto :fail
)

:check
echo.
echo [3/3] Kiem tra
"%PY%" -c "import TikTokLive, yt_dlp, pytchat, chat_downloader; print('   thu vien: ok')"
if errorlevel 1 (
  echo   Thieu thu vien. Thu:  Install.cmd -f
  goto :fail
)
"%PY%" -m pip check
if errorlevel 1 (
  echo   pip check bao phu thuoc lech nhau. Thu:  Install.cmd -f
  goto :fail
)

echo.
echo Xong. Chay tiep:
echo    web.cmd     overlay cho OBS o http://127.0.0.1:8770/
echo    run.cmd     chi hien trong cua so dong lenh
echo.
pause
exit /b 0

:fail
echo.
echo Chua cai xong. Xem documents\install.md de biet them.
echo.
pause
exit /b 1
