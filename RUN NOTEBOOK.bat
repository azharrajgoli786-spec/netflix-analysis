@echo off
cd /d "%~dp0"
echo Starting Netflix Analysis notebook...
python -m notebook notebooks\01-exploratory-analysis.ipynb
pause
