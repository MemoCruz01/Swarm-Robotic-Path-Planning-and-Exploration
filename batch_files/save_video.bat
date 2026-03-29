@echo off
REM Save Simulation as Video (GIF and MP4)
REM Double-click this file to save the swarm robotics simulation
REM Outputs to outputs/videos/

title Swarm Robotics - Video Saving Mode
cd /d "d:\A EMINENT Master\9 U Lisbon Munich\9 Swarm Robotics\Swarm Robotic Path Planning and Exploration"

echo ========================================
echo  SWARM ROBOTICS - SAVE VIDEO
echo ========================================
echo.
echo Starting simulation and saving video...
echo Output directory: outputs/videos/
echo.

C:\Users\joseg\AppData\Local\Microsoft\WindowsApps\python3.11.exe scripts\save_animation.py

pause
