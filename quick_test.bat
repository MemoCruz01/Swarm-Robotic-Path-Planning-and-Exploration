@echo off
REM Quick Test Simulation (200 iterations, no GUI)
REM Double-click this file to run quick test

title Swarm Robotics - Quick Test
cd /d "d:\A EMINENT Master\9 U Lisbon Munich\9 Swarm Robotics\Swarm Robotic Path Planning and Exploration"

echo ========================================
echo  SWARM ROBOTICS - QUICK TEST
echo ========================================
echo.
echo Running 200-iteration test...
echo.

C:\Users\joseg\AppData\Local\Microsoft\WindowsApps\python3.11.exe test_simulation.py

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.

pause
