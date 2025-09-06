@echo off
echo Fixing scene include files...

set SCENE_DIR=C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\scenes
set HELPERS_DIR=C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\helpers

REM 1. Fix scene header includes in all scene files
for %%f in ("%SCENE_DIR%\predator_scene_*.c") do (
    type nul > "%%f.new"
    echo #include "../predator_i.h" >> "%%f.new"
    echo #include "predator_scene.h" >> "%%f.new"
    echo. >> "%%f.new"
    
    findstr /v /b "#include \"../predator_i.h\"" "%%f" | findstr /v /b "#include \"predator_scene.h\"" >> "%%f.new"
    
    move /y "%%f.new" "%%f" > nul
    echo Fixed %%~nxf
)

REM 2. Fix notification sequence constant in car_tesla.c
if exist "%SCENE_DIR%\predator_scene_car_tesla.c" (
    type "%SCENE_DIR%\predator_scene_car_tesla.c" | find /v "sequence_blink_start_10" > "%SCENE_DIR%\predator_scene_car_tesla.c.new"
    move /y "%SCENE_DIR%\predator_scene_car_tesla.c.new" "%SCENE_DIR%\predator_scene_car_tesla.c" > nul
    
    type "%SCENE_DIR%\predator_scene_car_tesla.c" | find /v "notification_message(app->notifications, &" > "%SCENE_DIR%\predator_scene_car_tesla.c.new"
    move /y "%SCENE_DIR%\predator_scene_car_tesla.c.new" "%SCENE_DIR%\predator_scene_car_tesla.c" > nul
    
    echo Fixed notification sequence in predator_scene_car_tesla.c
)

echo All files fixed!
