import os
import glob
import re

# Directory containing scene files
scene_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\scenes"

# Process all scene files
scene_files = glob.glob(os.path.join(scene_dir, "predator_scene_*.c"))

for file_path in scene_files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add scene.h include if not present
    if '#include "predator_scene.h"' not in content:
        modified = content.replace('#include "../predator_i.h"', '#include "../predator_i.h"\n#include "predator_scene.h"')
        
        with open(file_path, 'w') as f:
            f.write(modified)
        
        print(f"Added scene header include to {os.path.basename(file_path)}")
    else:
        print(f"Scene header already present in {os.path.basename(file_path)}")

print("All scene files processed.")
