@echo off
REM Save Animation as GIF Video
REM Double-click this file to run simulation and save as swarm_simulation.gif

title Swarm Robotics - Save Video
cd /d "d:\A EMINENT Master\9 U Lisbon Munich\9 Swarm Robotics\Swarm Robotic Path Planning and Exploration"

echo ========================================
echo  SWARM ROBOTICS - SAVE VIDEO
echo ========================================
echo.
echo Starting simulation and saving as GIF...
echo This may take a few minutes...
echo.

C:\Users\joseg\AppData\Local\Microsoft\WindowsApps\python3.11.exe save_animation.py

echo.
echo ========================================
echo Video saved as: swarm_simulation.gif
echo ========================================
echo.

pause
