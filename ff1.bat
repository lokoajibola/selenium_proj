@echo off
call C:\ProgramData\anaconda3\Scripts\activate.bat base
cd "C:\Users\MY PC\bets"  // Navigate to the script directory
python sel_ff5.py      // Execute the script
pause                      // Keeps the Command Prompt window open after execution