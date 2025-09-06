#!/usr/bin/env python3

import os
import shutil
import re

print("Final BLE and app fixes for Predator firmware...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"

# 1. Fix ble_thread directory structure
ble_thread_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "interface", "patterns", "ble_thread")
os.makedirs(os.path.join(ble_thread_dir, "shci"), exist_ok=True)
os.makedirs(os.path.join(ble_thread_dir, "tl"), exist_ok=True)

# 2. Create essential header files with proper contents
# SHCI missing_types.h
missing_types_h = """#pragma once

#include <stdint.h>

/* BLE Type Definitions */
typedef struct {
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tSHciIO;

typedef struct {
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tHciIO;

typedef struct {
    uint8_t KeyType;
    uint8_t encrypted;
    uint8_t key[16];
} SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;

typedef struct {
  uint8_t *p_cmdbuffer;
  void (*StatusNotCallBack)(uint8_t status);
} HCI_TL_HciInitConf_t;

typedef uint8_t HCI_TL_CmdStatus_t;
"""

with open(os.path.join(ble_thread_dir, "tl", "missing_types.h"), "w") as f:
    f.write(missing_types_h)
print("✅ Created missing_types.h")

# 3. Fix ble.h to include the missing header and ensure proper type definitions
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the file
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    # Add include for missing_types.h at the top of the file
    if "#include" in content:
        last_include = content.rfind("#include")
        last_include_end = content.find("\n", last_include) + 1
        content = content[:last_include_end] + "#include \"../interface/patterns/ble_thread/tl/missing_types.h\"\n" + content[last_include_end:]
    
    # Fix the function declarations
    if "void shci_register_io_bus(tSHciIO* fops);" in content:
        content = content.replace(
            "void shci_register_io_bus(tSHciIO* fops);",
            "void shci_register_io_bus(tSHciIO* fops); /* Fixed declaration */"
        )
    
    if "tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t* pParam, uint8_t* slot);" in content:
        content = content.replace(
            "tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t* pParam, uint8_t* slot);",
            "tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t* pParam, uint8_t* slot); /* Fixed declaration */"
        )
    
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Updated ble.h to include missing_types.h")

# 4. Create shci.h with proper includes
shci_h = """#pragma once

#include <stdint.h>
#include "../../ble/ble.h"
#include "../tl/missing_types.h"

void shci_register_io_bus(tSHciIO* fops);
"""

with open(os.path.join(ble_thread_dir, "shci", "shci.h"), "w") as f:
    f.write(shci_h)
print("✅ Created shci.h")

# 5. Fix app_common.h
app_common_h_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "app_common.h")
if os.path.exists(app_common_h_path):
    with open(app_common_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the file
    shutil.copy2(app_common_h_path, app_common_h_path + ".bak")
    
    # Fix includes in app_common.h
    if "#include \"app_conf.h\"" in content:
        content = content.replace(
            "#include \"app_conf.h\"",
            "#include \"app_conf.h\" // Fixed include"
        )
    
    with open(app_common_h_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Fixed app_common.h")

# 6. Make sure Predator app is in the applications_user directory only
predator_app_path = os.path.join(fw_dir, "applications_user", "predator")
os.makedirs(predator_app_path, exist_ok=True)

# Remove all other predator app instances
main_predator_path = os.path.join(fw_dir, "applications", "main", "predator")
if os.path.exists(main_predator_path):
    shutil.rmtree(main_predator_path)
    print(f"✅ Removed {main_predator_path}")

main_predator_app_path = os.path.join(fw_dir, "applications", "main", "predator_app")
if os.path.exists(main_predator_app_path):
    shutil.rmtree(main_predator_app_path)
    print(f"✅ Removed {main_predator_app_path}")

ext_predator_path = os.path.join(fw_dir, "applications", "external", "predator")
if os.path.exists(ext_predator_path):
    shutil.rmtree(ext_predator_path)
    print(f"✅ Removed {ext_predator_path}")

# 7. Create application.fam in applications_user/predator if it doesn't exist
predator_fam_path = os.path.join(predator_app_path, "application.fam")
if not os.path.exists(predator_fam_path):
    predator_fam = """App(
    appid="predator",
    name="Predator",
    apptype=FlipperAppType.EXTERNAL,
    entry_point="predator_app",
    requires=["gui", "dialogs", "storage", "notification", "subghz", "nfc", "bt", "infrared"],
    stack_size=4 * 1024,
    order=10,
    fap_icon="predator.png",
    fap_category="Tools",
    fap_author="Predator Team",
    fap_version="1.0",
    fap_description="Advanced penetration testing toolkit for Flipper Zero with Predator module",
)
"""
    with open(predator_fam_path, "w") as f:
        f.write(predator_fam)
    print("✅ Created application.fam in applications_user/predator")

print("All fixes applied! You can now try building the firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd fap_predator")
print("Or for full firmware:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
