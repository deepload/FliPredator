#!/usr/bin/env python3

import os
import glob
import re
import shutil

def main():
    print("Adding missing includes to Predator scene files...")
    
    # Source and target paths
    source_dir = os.path.join("C:", "Projects", "Predator", "predator_app")
    firmware_dir = os.path.join("C:", "Projects", "Predator", "flipperzero-firmware-wPlugins")
    target_dir = os.path.join(firmware_dir, "applications", "main", "predator_app")
    
    # Create target directories if they don't exist
    os.makedirs(os.path.join(target_dir, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "helpers"), exist_ok=True)
    
    # Fix scene files
    scene_files = glob.glob(os.path.join(source_dir, "scenes", "*.c"))
    for scene_file in scene_files:
        scene_name = os.path.basename(scene_file)
        target_scene_file = os.path.join(target_dir, "scenes", scene_name)
        
        with open(scene_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Check what function calls are used to determine needed includes
        needs_esp32 = "predator_esp32_" in content and "../helpers/predator_esp32.h" not in content
        needs_gps = "predator_gps_" in content and "../helpers/predator_gps.h" not in content
        needs_subghz = "predator_subghz_" in content and "../helpers/predator_subghz.h" not in content
        
        # Make sure basic includes are there
        if "#include \"../predator_i.h\"" not in content:
            content = "#include \"../predator_i.h\"\n" + content
        
        if "#include \"predator_scene.h\"" not in content:
            content = content.replace("#include \"../predator_i.h\"", 
                                     "#include \"../predator_i.h\"\n#include \"predator_scene.h\"")
        
        # Add helper includes if needed
        helper_includes = ""
        if needs_esp32:
            helper_includes += "#include \"../helpers/predator_esp32.h\"\n"
        if needs_gps:
            helper_includes += "#include \"../helpers/predator_gps.h\"\n"
        if needs_subghz:
            helper_includes += "#include \"../helpers/predator_subghz.h\"\n"
        
        if helper_includes:
            content = content.replace("#include \"predator_scene.h\"", 
                                     "#include \"predator_scene.h\"\n" + helper_includes)
        
        # Write fixed content back to source file
        with open(scene_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Also copy to target directory
        with open(target_scene_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✓ Fixed {scene_name}")
    
    print("All scene files fixed successfully!")

if __name__ == "__main__":
    main()
