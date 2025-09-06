#!/usr/bin/env python3

import os
import glob
import re
import shutil

def main():
    print("Fixing Predator app compilation errors...")
    
    source_app_dir = os.path.join("C:", "Projects", "Predator", "predator_app")
    firmware_dir = os.path.join("C:", "Projects", "Predator", "flipperzero-firmware-wPlugins")
    target_app_dir = os.path.join(firmware_dir, "applications", "main", "predator_app")
    
    # Make sure target directories exist
    os.makedirs(os.path.join(target_app_dir, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(target_app_dir, "helpers"), exist_ok=True)
    
    # 1. Create application.fam manifest
    create_application_manifest(target_app_dir)
    
    # 2. Fix predator.c to use correct predator_uart_init signature
    fix_predator_c(source_app_dir, target_app_dir)
    
    # 3. Fix all scene files to include proper headers
    fix_scene_files(source_app_dir, target_app_dir)
    
    # 4. Fix helper modules to have proper declarations
    fix_helper_modules(source_app_dir, target_app_dir)
    
    print("\nAll fixes applied successfully! Try building the firmware now.")
    print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd fap_predator")

def create_application_manifest(target_dir):
    """Create application.fam manifest file"""
    manifest_content = """App(
    appid="predator",
    name="Predator",
    apptype=FlipperAppType.EXTERNAL,
    entry_point="predator_app",
    requires=["gui"],
    stack_size=2 * 1024,
    fap_category="Tools",
    fap_icon="predator_10px.png",
    fap_icon_assets="assets",
    fap_author="ClaraCrazy & Flipper-XFW Team",
    fap_weburl="https://github.com/ClaraCrazy/Flipper-Xtreme",
    fap_version=(1, 1),
    fap_description="All-in-one RF & wireless hacking toolkit",
)
"""
    with open(os.path.join(target_dir, "application.fam"), "w") as f:
        f.write(manifest_content)
    print("✅ Created application.fam manifest")

def fix_predator_c(source_dir, target_dir):
    """Fix predator.c to use correct predator_uart_init signature"""
    predator_c_path = os.path.join(source_dir, "predator.c")
    target_predator_c_path = os.path.join(target_dir, "predator.c")
    
    with open(predator_c_path, "r") as f:
        content = f.read()
    
    # Fix UART initialization calls to match the header
    fixed_content = re.sub(
        r'app->esp32_uart = predator_uart_init\((PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, PREDATOR_ESP32_UART_BAUD)(, predator_esp32_rx_callback, app)?\);',
        r'app->esp32_uart = predator_uart_init(PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, PREDATOR_ESP32_UART_BAUD, predator_esp32_rx_callback, app);',
        content
    )
    
    fixed_content = re.sub(
        r'app->gps_uart = predator_uart_init\((PREDATOR_GPS_UART_TX_PIN, PREDATOR_GPS_UART_RX_PIN, PREDATOR_GPS_UART_BAUD)(, predator_gps_rx_callback, app)?\);',
        r'app->gps_uart = predator_uart_init(PREDATOR_GPS_UART_TX_PIN, PREDATOR_GPS_UART_RX_PIN, PREDATOR_GPS_UART_BAUD, predator_gps_rx_callback, app);',
        fixed_content
    )
    
    # Add missing UART callback function if needed
    if "predator_uart_set_rx_callback" in fixed_content and "app->esp32_uart, predator_esp32_rx_callback, app" in fixed_content:
        fixed_content = fixed_content.replace(
            "predator_uart_set_rx_callback(app->esp32_uart, predator_esp32_rx_callback, app);",
            "// Callback already set in predator_uart_init"
        )
    
    with open(target_predator_c_path, "w") as f:
        f.write(fixed_content)
    print("✅ Fixed predator.c UART initialization")

def fix_scene_files(source_dir, target_dir):
    """Fix all scene files to include helper headers"""
    scene_files = glob.glob(os.path.join(source_dir, "scenes", "*.c"))
    
    for scene_file in scene_files:
        scene_name = os.path.basename(scene_file)
        target_scene_file = os.path.join(target_dir, "scenes", scene_name)
        
        with open(scene_file, "r") as f:
            content = f.read()
        
        # Add necessary includes based on function calls
        needs_esp32 = "predator_esp32_" in content
        needs_gps = "predator_gps_" in content
        needs_subghz = "predator_subghz_" in content
        
        # Create include headers
        includes = ['#include "../predator_i.h"', '#include "predator_scene.h"']
        
        if needs_esp32:
            includes.append('#include "../helpers/predator_esp32.h"')
        if needs_gps:
            includes.append('#include "../helpers/predator_gps.h"')
        if needs_subghz:
            includes.append('#include "../helpers/predator_subghz.h"')
        
        # Get function body (everything after includes)
        lines = content.split("\n")
        non_include_line = 0
        for i, line in enumerate(lines):
            if not line.strip().startswith("#include") and line.strip():
                non_include_line = i
                break
        
        # Create new content with proper includes
        new_content = "\n".join(includes) + "\n\n" + "\n".join(lines[non_include_line:])
        
        with open(target_scene_file, "w") as f:
            f.write(new_content)
        
        print(f"✅ Fixed {scene_name}")

def fix_helper_modules(source_dir, target_dir):
    """Fix helper modules to have proper function declarations"""
    # Copy and fix ESP32 helper
    esp32_c_source = os.path.join(source_dir, "helpers", "predator_esp32.c")
    esp32_h_source = os.path.join(source_dir, "helpers", "predator_esp32.h")
    esp32_c_target = os.path.join(target_dir, "helpers", "predator_esp32.c")
    esp32_h_target = os.path.join(target_dir, "helpers", "predator_esp32.h")
    
    # Copy ESP32 header
    shutil.copy2(esp32_h_source, esp32_h_target)
    
    if os.path.exists(esp32_c_source):
        with open(esp32_c_source, "r") as f:
            content = f.read()
        
        # Make sure it includes its own header
        if '#include "predator_esp32.h"' not in content:
            content = '#include "predator_esp32.h"\n' + content
        
        with open(esp32_c_target, "w") as f:
            f.write(content)
    
    # Copy and fix GPS helper
    gps_c_source = os.path.join(source_dir, "helpers", "predator_gps.c")
    gps_h_source = os.path.join(source_dir, "helpers", "predator_gps.h")
    gps_c_target = os.path.join(target_dir, "helpers", "predator_gps.c")
    gps_h_target = os.path.join(target_dir, "helpers", "predator_gps.h")
    
    # Copy GPS header
    shutil.copy2(gps_h_source, gps_h_target)
    
    if os.path.exists(gps_c_source):
        with open(gps_c_source, "r") as f:
            content = f.read()
        
        # Make sure it includes its own header
        if '#include "predator_gps.h"' not in content:
            content = '#include "predator_gps.h"\n' + content
        
        with open(gps_c_target, "w") as f:
            f.write(content)
    
    # Copy and fix SubGhz helper
    subghz_c_source = os.path.join(source_dir, "helpers", "predator_subghz.c")
    subghz_h_source = os.path.join(source_dir, "helpers", "predator_subghz.h")
    subghz_c_target = os.path.join(target_dir, "helpers", "predator_subghz.c")
    subghz_h_target = os.path.join(target_dir, "helpers", "predator_subghz.h")
    
    # Copy SubGhz header
    shutil.copy2(subghz_h_source, subghz_h_target)
    
    if os.path.exists(subghz_c_source):
        with open(subghz_c_source, "r") as f:
            content = f.read()
        
        # Make sure it includes its own header
        if '#include "predator_subghz.h"' not in content:
            content = '#include "predator_subghz.h"\n' + content
        
        with open(subghz_c_target, "w") as f:
            f.write(content)
    
    # Copy UART implementation and header
    uart_c_source = os.path.join(source_dir, "predator_uart.c")
    uart_h_source = os.path.join(source_dir, "predator_uart.h")
    uart_c_target = os.path.join(target_dir, "predator_uart.c")
    uart_h_target = os.path.join(target_dir, "predator_uart.h")
    
    shutil.copy2(uart_h_source, uart_h_target)
    shutil.copy2(uart_c_source, uart_c_target)
    
    print("✅ Fixed helper module includes and declarations")

if __name__ == "__main__":
    main()
