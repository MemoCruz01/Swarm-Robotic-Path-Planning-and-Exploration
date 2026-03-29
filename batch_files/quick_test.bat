@echo off
REM Quick Test (No GUI)
REM Double-click this file to run a fast test without visualization
REM Outputs logs to outputs/logs/

title Swarm Robotics - Quick Test
cd /d "d:\A EMINENT Master\9 U Lisbon Munich\9 Swarm Robotics\Swarm Robotic Path Planning and Exploration"

echo ========================================
echo  SWARM ROBOTICS - QUICK TEST
echo ========================================
echo.
echo Running 200-iteration test (no GUI)...
echo.

C:\Users\joseg\AppData\Local\Microsoft\WindowsApps\python3.11.exe scripts\test_simulation.py

pause
