import os
import re

scene_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\scenes"
scene_files = [f for f in os.listdir(scene_dir) if f.endswith(".c") and f.startswith("predator_scene_")]

for file_name in scene_files:
    file_path = os.path.join(scene_dir, file_name)
    
    with open(file_path, "r") as file:
        content = file.read()
    
    # Check if the scene header is already included
    if '#include "predator_scene.h"' not in content:
        # Add the include after predator_i.h
        new_content = re.sub(
            r'(#include "../predator_i.h")', 
            r'\1\n#include "predator_scene.h"', 
            content
        )
        
        with open(file_path, "w") as file:
            file.write(new_content)
        
        print(f"Added scene header to {file_name}")
    else:
        print(f"Scene header already present in {file_name}")

print("Done processing scene files")
