import os
import glob

def fix_scene_includes():
    scene_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app\scenes"
    scene_files = glob.glob(os.path.join(scene_dir, "predator_scene_*.c"))
    
    for file_path in scene_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Remove duplicate scene header includes if any
        if content.count('#include "predator_scene.h"') > 1:
            parts = content.split('#include "predator_scene.h"', 1)
            content = parts[0] + '#include "predator_scene.h"' + parts[1].replace('#include "predator_scene.h"', '')
        
        # Add scene header include if missing
        if '#include "predator_scene.h"' not in content:
            content = content.replace('#include "../predator_i.h"', 
                                      '#include "../predator_i.h"\n#include "predator_scene.h"')
            
        # Fix float to double promotion warnings
        content = content.replace('app->latitude, app->longitude', '(double)app->latitude, (double)app->longitude')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {os.path.basename(file_path)}")

if __name__ == "__main__":
    fix_scene_includes()
    print("Done! Fixed scene includes and float promotion issues.")
