@echo off
echo Building MEGA Account Generator...

set SITE_PACKAGES=C:\Users\Bruno\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages
set CTK_PATH=%SITE_PACKAGES%\customtkinter
set R_USER_PATH=%SITE_PACKAGES%\random_username

python -m PyInstaller --noconsole --onefile ^
    --add-data "%CTK_PATH%;customtkinter/" ^
    --add-data "%R_USER_PATH%;random_username/" ^
    --add-data "logo.ico;." ^
    --add-data "logo.png;." ^
    --add-data "megatools;megatools" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "babel.numbers" ^
    --hidden-import "openpyxl" ^
    --hidden-import "openpyxl.cell._writer" ^
    --hidden-import "openpyxl.workbook._writer" ^
    --hidden-import "openpyxl.worksheet._writer" ^
    --hidden-import "apscheduler" ^
    --hidden-import "apscheduler.triggers.interval" ^
    --icon "logo.ico" ^
    --name "MEGA-Generator" ^
    gui.py

echo Build complete! Check the 'dist' folder.
pause
