@echo off
setlocal enabledelayedexpansion

set SCENE_DIR=C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\scenes
set FILES=%SCENE_DIR%\predator_scene_*.c

for %%F in (%FILES%) do (
    echo Processing %%F
    type "%%F" > temp.txt
    
    findstr /c:"#include \"predator_scene.h\"" "%%F" >nul
    if errorlevel 1 (
        echo Adding scene include to %%F
        (
            echo #include "../predator_i.h"
            echo #include "predator_scene.h"
            echo.
            findstr /v "#include \"../predator_i.h\"" temp.txt
        ) > "%%F.new"
        move /y "%%F.new" "%%F" >nul
    ) else (
        echo Scene include already exists in %%F
    )
)

del temp.txt
echo All files processed.
