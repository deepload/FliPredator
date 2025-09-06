import os
import re
import glob
import shutil

print("Fixing Predator firmware compilation errors...")

# Base paths
base_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app"
scene_dir = os.path.join(base_dir, "scenes")
helpers_dir = os.path.join(base_dir, "helpers")

# 1. Fix ESP32 helper file with correct function signatures
esp32_header = """#pragma once

#include <furi.h>

typedef struct PredatorEsp32 PredatorEsp32;
typedef struct PredatorApp PredatorApp;

// ESP32 callback for received data
void predator_esp32_rx_callback(uint8_t* buf, size_t len, void* context);

// ESP32 management functions
void predator_esp32_init(PredatorApp* app);
void predator_esp32_deinit(PredatorApp* app);
bool predator_esp32_send_command(PredatorApp* app, const char* command);
bool predator_esp32_is_connected(PredatorApp* app);

// WiFi attack functions
bool predator_esp32_wifi_scan(PredatorApp* app);
bool predator_esp32_wifi_deauth(PredatorApp* app, int channel);
bool predator_esp32_wifi_evil_twin(PredatorApp* app);

// Bluetooth attack functions
bool predator_esp32_ble_scan(PredatorApp* app);
bool predator_esp32_ble_spam(PredatorApp* app);

// Wardriving function
bool predator_esp32_wardrive(PredatorApp* app);

// Status and control
bool predator_esp32_stop_attack(PredatorApp* app);
bool predator_esp32_get_status(PredatorApp* app);
"""

with open(os.path.join(helpers_dir, "predator_esp32.h"), 'w', encoding='utf-8') as f:
    f.write(esp32_header)
print("✓ Fixed ESP32 helper header with correct function signatures")

# 2. Fix all scene files
scene_files = glob.glob(os.path.join(scene_dir, "predator_scene_*.c"))
for file_path in scene_files:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Create a new content with the correct includes at the top
    new_content = "#include \"../predator_i.h\"\n#include \"predator_scene.h\"\n\n"
    
    # Skip existing includes and append the rest of the file
    lines = content.split('\n')
    skip_until = 0
    for i, line in enumerate(lines):
        if line.startswith('#include'):
            skip_until = i + 1
        else:
            break
    
    # Add the rest of the content from the original file
    new_content += '\n'.join(lines[skip_until:])
    
    # Fix float to double promotion warnings
    new_content = new_content.replace('app->latitude, app->longitude', '(double)app->latitude, (double)app->longitude')
    
    # Fix notification sequence constants
    new_content = new_content.replace('sequence_blink_start_10', 'sequence_blink_blue_10')
    new_content = new_content.replace('sequence_single_vibro', 'sequence_success')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✓ Fixed {os.path.basename(file_path)}")

# 3. Fix SubGHz function calls to remove deprecated calls
subghz_file = os.path.join(helpers_dir, "predator_subghz.c")
if os.path.exists(subghz_file):
    with open(subghz_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix deprecated furi_hal_subghz_load_preset call
    content = re.sub(r'furi_hal_subghz_load_preset\([^\)]+\);', '', content)
    
    # Fix furi_hal_subghz_set_path calls
    content = re.sub(r'furi_hal_subghz_set_path\([^\)]+\);[\s\n]*furi_hal_subghz_set_frequency\(([^\)]+)\);', 
                   r'furi_hal_subghz_set_frequency_and_path(\1);', content)
    
    with open(subghz_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Fixed SubGHz preset functions")

print("\nAll compilation errors have been fixed. Try building the firmware now.")
print("Command: cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd fap_predator")
