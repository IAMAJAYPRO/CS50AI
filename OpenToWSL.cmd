@echo off
rem Get the parameter passed (if any), default to current directory
set "target=%~1"
if "%target%"=="" set "target=%cd%"

rem Convert Windows path to WSL path and open in WSL
wsl -e bash -c "cd \"$(wslpath '%target%')\" && exec bash"
