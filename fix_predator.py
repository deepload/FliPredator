import os
import re
import glob

# Base paths
base_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins\applications\main\predator_app"
scene_dir = os.path.join(base_dir, "scenes")
helpers_dir = os.path.join(base_dir, "helpers")

print("Starting Predator firmware fixes...")

# 1. Fix ESP32 header with correct function signatures
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
print("Fixed ESP32 helper header function signatures")

# 2. Fix scene includes in all scene files
scene_files = glob.glob(os.path.join(scene_dir, "predator_scene_*.c"))
for file_path in scene_files:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix double includes if they exist
    content = re.sub(r'#include "predator_scene.h"\s+#include "predator_scene.h"', '#include "predator_scene.h"', content)
    
    # Add scene header include if missing
    if '#include "predator_scene.h"' not in content:
        content = content.replace('#include "../predator_i.h"', '#include "../predator_i.h"\n#include "predator_scene.h"')
    
    # Fix float to double promotion warnings
    content = re.sub(r'app->latitude, app->longitude', '(double)app->latitude, (double)app->longitude', content)
    
    # Fix notification sequence constant
    content = content.replace('sequence_blink_start_10', 'sequence_blink_blue_10')
    content = content.replace('sequence_single_vibro', 'sequence_success')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {os.path.basename(file_path)}")

# 3. Fix SubGHz preset function
subghz_file = os.path.join(helpers_dir, "predator_subghz.c")
if os.path.exists(subghz_file):
    with open(subghz_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix deprecated furi_hal_subghz_load_preset call
    if "furi_hal_subghz_load_preset" in content:
        # Remove the line with the deprecated call
        content = re.sub(r'.*furi_hal_subghz_load_preset.*\n', '', content)
        # Make sure we have the proper settings
        if "furi_hal_subghz_set_tx_power" not in content:
            content = content.replace("furi_hal_subghz_reset();", "furi_hal_subghz_reset();\n    furi_hal_subghz_set_tx_power(10);")
    
    with open(subghz_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed SubGHz preset functions")

print("All fixes applied! Ready to compile.")
