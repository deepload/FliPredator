import os
import re
import glob
import shutil

# Base paths
base_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app"
scene_dir = os.path.join(base_path, "scenes")
helper_dir = os.path.join(base_path, "helpers")

# 1. Fix scene header includes
scene_files = glob.glob(os.path.join(scene_dir, "predator_scene_*.c"))
for file_path in scene_files:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if '#include "predator_scene.h"' not in content:
        modified = content.replace('#include "../predator_i.h"', '#include "../predator_i.h"\n#include "predator_scene.h"')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        print(f"Added scene header to {os.path.basename(file_path)}")

# 2. Fix notification sequence constants
files_with_notifications = [
    os.path.join(scene_dir, "predator_scene_car_tesla.c"),
    os.path.join(scene_dir, "predator_scene_rfid_bruteforce.c")
]

for file_path in files_with_notifications:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace outdated sequence constants
        modified = content.replace('&sequence_blink_start_10', '&sequence_blink_blue_10')
        modified = modified.replace('&sequence_single_vibro', '&sequence_success')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        print(f"Fixed notification sequences in {os.path.basename(file_path)}")

# 3. Fix float to double promotion warnings in GPS tracker
gps_tracker_path = os.path.join(scene_dir, "predator_scene_gps_tracker.c")
if os.path.exists(gps_tracker_path):
    with open(gps_tracker_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add explicit casting to double for float parameters
    modified = re.sub(
        r'app->latitude, app->longitude', 
        '(double)app->latitude, (double)app->longitude', 
        content
    )
    
    with open(gps_tracker_path, 'w', encoding='utf-8') as f:
        f.write(modified)
    
    print("Fixed float to double promotion in GPS tracker")

# 4. Fix wardriving file too
wardriving_path = os.path.join(scene_dir, "predator_scene_wardriving.c")
if os.path.exists(wardriving_path):
    with open(wardriving_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add explicit casting to double for float parameters
    modified = re.sub(
        r'app->latitude, app->longitude', 
        '(double)app->latitude, (double)app->longitude', 
        content
    )
    
    with open(wardriving_path, 'w', encoding='utf-8') as f:
        f.write(modified)
    
    print("Fixed float to double promotion in wardriving")

print("All fixes applied. Ready for compilation.")
