@echo off
rem The same launcher with the overlay switched on, so this is a thing you can
rem double-click. It calls run.cmd rather than repeating the venv bootstrap,
rem so there is one copy of that and it cannot drift.
rem
rem OBS: Sources > + > Browser, URL = the address printed below, and leave
rem Custom CSS empty -- the page is already transparent.
call "%~dp0run.cmd" --web %*
