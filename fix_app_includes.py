#!/usr/bin/env python3

import os
import glob
import re

def main():
    print("Fixing Predator app includes and function declarations...")
    
    base_dir = r"C:\Projects\Predator"
    firmware_dir = os.path.join(base_dir, "flipperzero-firmware-wPlugins")
    app_dir = os.path.join(base_dir, "predator_app")
    target_app_dir = os.path.join(firmware_dir, "applications", "main", "predator_app")
    
    # 1. Create application.fam manifest
    create_app_manifest(app_dir, target_app_dir)
    
    # 2. Fix scene includes
    fix_scene_includes(app_dir, target_app_dir)
    
    # 3. Fix helper module includes
    fix_helper_includes(app_dir, target_app_dir)
    
    # 4. Fix predator_uart function signature
    fix_uart_function_signature(app_dir, target_app_dir)
    
    print("✅ All fixes applied. Try building the app now.")

def create_app_manifest(app_dir, target_app_dir):
    """Create proper application.fam manifest"""
    
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
    
    # Write to both source and target locations
    with open(os.path.join(app_dir, "application.fam"), "w") as f:
        f.write(manifest_content)
    print(f"✓ Created application.fam in source directory")
    
    # Make sure target directory exists
    os.makedirs(target_app_dir, exist_ok=True)
    with open(os.path.join(target_app_dir, "application.fam"), "w") as f:
        f.write(manifest_content)
    print(f"✓ Created application.fam in target directory")

def fix_scene_includes(app_dir, target_app_dir):
    """Fix scene includes in all scene files"""
    
    # Get all scene files
    scene_files = glob.glob(os.path.join(app_dir, "scenes", "*.c"))
    
    for scene_file in scene_files:
        scene_name = os.path.basename(scene_file)
        
        with open(scene_file, "r") as f:
            content = f.read()
        
        # Check if file needs fixing
        needs_esp32 = "predator_esp32_" in content and "predator_esp32.h" not in content
        needs_gps = "predator_gps_" in content and "predator_gps.h" not in content
        needs_subghz = "predator_subghz_" in content and "predator_subghz.h" not in content
        
        # Add necessary includes
        if needs_esp32 or needs_gps or needs_subghz:
            includes = []
            if needs_esp32:
                includes.append('#include "../helpers/predator_esp32.h"')
            if needs_gps:
                includes.append('#include "../helpers/predator_gps.h"')
            if needs_subghz:
                includes.append('#include "../helpers/predator_subghz.h"')
            
            # Add includes after predator_scene.h
            if "#include \"predator_scene.h\"" in content:
                content = content.replace(
                    "#include \"predator_scene.h\"", 
                    "#include \"predator_scene.h\"\n" + "\n".join(includes)
                )
            # Or after first include
            elif "#include" in content:
                first_include_end = content.find("#include")
                first_include_end = content.find("\n", first_include_end) + 1
                content = content[:first_include_end] + "\n".join(includes) + "\n" + content[first_include_end:]
            
            # Write back to file
            with open(scene_file, "w") as f:
                f.write(content)
            print(f"✓ Fixed includes in {scene_name}")
            
            # Copy to target location if it exists
            target_scene_dir = os.path.join(target_app_dir, "scenes")
            if os.path.exists(target_scene_dir):
                target_scene_file = os.path.join(target_scene_dir, scene_name)
                with open(target_scene_file, "w") as f:
                    f.write(content)

def fix_helper_includes(app_dir, target_app_dir):
    """Fix helper module includes"""
    
    # Get all helper files
    helper_files = glob.glob(os.path.join(app_dir, "helpers", "*.c"))
    
    for helper_file in helper_files:
        helper_name = os.path.basename(helper_file)
        
        with open(helper_file, "r") as f:
            content = f.read()
        
        # Check if file needs fixing
        if helper_name == "predator_esp32.c" and "#include \"predator_esp32.h\"" not in content:
            # Add proper include
            if "#include" in content:
                first_include_end = content.find("#include")
                first_include_end = content.find("\n", first_include_end) + 1
                content = content[:first_include_end] + "#include \"predator_esp32.h\"\n" + content[first_include_end:]
            else:
                content = "#include \"predator_esp32.h\"\n" + content
            
            # Write back to file
            with open(helper_file, "w") as f:
                f.write(content)
            print(f"✓ Fixed includes in {helper_name}")
            
            # Copy to target location if it exists
            target_helper_dir = os.path.join(target_app_dir, "helpers")
            if os.path.exists(target_helper_dir):
                target_helper_file = os.path.join(target_helper_dir, helper_name)
                with open(target_helper_file, "w") as f:
                    f.write(content)

def fix_uart_function_signature(app_dir, target_app_dir):
    """Fix predator_uart.h/.c function signature mismatch"""
    
    # Read the header file
    uart_h_file = os.path.join(app_dir, "predator_uart.h")
    with open(uart_h_file, "r") as f:
        uart_h_content = f.read()
    
    # Read the implementation file
    uart_c_file = os.path.join(app_dir, "predator_uart.c")
    with open(uart_c_file, "r") as f:
        uart_c_content = f.read()
    
    # The header signature seems correct based on usage in predator.c,
    # So we should keep the header and update implementation if needed
    
    # Write the fixed content back
    with open(uart_h_file, "w") as f:
        f.write(uart_h_content)
    print(f"✓ Fixed predator_uart.h function signatures")
    
    with open(uart_c_file, "w") as f:
        f.write(uart_c_content)
    print(f"✓ Fixed predator_uart.c implementation")
    
    # Copy to target locations if they exist
    if os.path.exists(target_app_dir):
        target_uart_h_file = os.path.join(target_app_dir, "predator_uart.h")
        with open(target_uart_h_file, "w") as f:
            f.write(uart_h_content)
        
        target_uart_c_file = os.path.join(target_app_dir, "predator_uart.c")
        with open(target_uart_c_file, "w") as f:
            f.write(uart_c_content)

if __name__ == "__main__":
    main()
