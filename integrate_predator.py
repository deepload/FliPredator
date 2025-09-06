#!/usr/bin/env python3

import os
import shutil
import glob
import re

print("Integrating Predator app into Flipper Zero firmware...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
predator_dir = r"C:\Projects\Predator\predator_app"

# 1. First, ensure we have a clean integration environment
print("\n1. Setting up integration environment...")

# Create proper directory in applications/main for built-in app (not as external .fap)
app_dir = os.path.join(fw_dir, "applications", "main", "predator")
os.makedirs(app_dir, exist_ok=True)

# Remove any duplicate app directories that might cause conflicts
duplicate_dirs = [
    os.path.join(fw_dir, "applications", "main", "predator_app"),
    os.path.join(fw_dir, "applications", "external", "predator"),
    os.path.join(fw_dir, "applications_user", "predator")
]

for dir_path in duplicate_dirs:
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"✓ Removed duplicate directory: {dir_path}")
        except Exception as e:
            print(f"⚠️ Failed to remove {dir_path}: {e}")

# 2. Copy all Predator app files to the main applications directory
print("\n2. Copying Predator app files to firmware...")

# Copy all files from predator_app to the main application directory
predator_files = glob.glob(os.path.join(predator_dir, "*.*"))
for file_path in predator_files:
    if os.path.isfile(file_path) and not file_path.endswith(".fap"):
        target_path = os.path.join(app_dir, os.path.basename(file_path))
        shutil.copy2(file_path, target_path)
        print(f"✓ Copied {os.path.basename(file_path)}")

# Create helpers directory and copy helper files
helpers_dir = os.path.join(app_dir, "helpers")
os.makedirs(helpers_dir, exist_ok=True)

helper_files = glob.glob(os.path.join(predator_dir, "helpers", "*.*"))
for file_path in helper_files:
    if os.path.isfile(file_path):
        target_path = os.path.join(helpers_dir, os.path.basename(file_path))
        shutil.copy2(file_path, target_path)
        print(f"✓ Copied helper: {os.path.basename(file_path)}")

# Create scenes directory and copy scene files
scenes_dir = os.path.join(app_dir, "scenes")
os.makedirs(scenes_dir, exist_ok=True)

scene_files = glob.glob(os.path.join(predator_dir, "scenes", "*.*"))
for file_path in scene_files:
    if os.path.isfile(file_path):
        target_path = os.path.join(scenes_dir, os.path.basename(file_path))
        shutil.copy2(file_path, target_path)
        print(f"✓ Copied scene: {os.path.basename(file_path)}")

# 3. Create proper application.fam for built-in app (different from external .fap)
print("\n3. Creating application manifest...")

application_fam = """App(
    appid="predator",
    name="Predator",
    apptype=FlipperAppType.APP,  # Built-in app, not external
    entry_point="predator_app",
    stack_size=4 * 1024,
    icon="A_Infrared_14",
    order=50,
    requires=[
        "gui",
        "dialogs", 
        "storage",
        "notification",
        "subghz",
        "nfc",
        "bt",
        "infrared",
    ],
)
"""

with open(os.path.join(app_dir, "application.fam"), "w") as f:
    f.write(application_fam)
print("✓ Created application.fam manifest")

# 4. Fix includes in all Predator app files
print("\n4. Fixing includes in Predator files...")

# Fix scene files includes
for scene_file in glob.glob(os.path.join(scenes_dir, "predator_scene_*.c")):
    with open(scene_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add scene.h include if not present
    if '#include "predator_scene.h"' not in content:
        modified = content.replace('#include "../predator_i.h"', '#include "../predator_i.h"\n#include "predator_scene.h"')
        
        with open(scene_file, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        print(f"✓ Added scene header include to {os.path.basename(scene_file)}")

# 5. Fix UART initialization in predator.c
print("\n5. Fixing UART initialization...")

predator_c_path = os.path.join(app_dir, "predator.c")
if os.path.exists(predator_c_path):
    with open(predator_c_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if "predator_uart_init" in content and "predator_esp32_rx_callback" in content:
        # Make sure the ESP32 UART initialization has the right callback parameter
        if "app->esp32_uart = predator_uart_init(PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, PREDATOR_ESP32_UART_BAUD)" in content:
            content = content.replace(
                "app->esp32_uart = predator_uart_init(PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, PREDATOR_ESP32_UART_BAUD)",
                "app->esp32_uart = predator_uart_init(PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, PREDATOR_ESP32_UART_BAUD, predator_esp32_rx_callback, app)"
            )
            print("✓ Fixed ESP32 UART initialization in predator.c")
        
        # Make sure the GPS UART initialization has the right callback parameter
        if "app->gps_uart = predator_uart_init(PREDATOR_GPS_UART_TX_PIN, PREDATOR_GPS_UART_RX_PIN, PREDATOR_GPS_UART_BAUD)" in content:
            content = content.replace(
                "app->gps_uart = predator_uart_init(PREDATOR_GPS_UART_TX_PIN, PREDATOR_GPS_UART_RX_PIN, PREDATOR_GPS_UART_BAUD)",
                "app->gps_uart = predator_uart_init(PREDATOR_GPS_UART_TX_PIN, PREDATOR_GPS_UART_RX_PIN, PREDATOR_GPS_UART_BAUD, predator_gps_rx_callback, app)"
            )
            print("✓ Fixed GPS UART initialization in predator.c")
        
        # Write the changes back
        with open(predator_c_path, 'w', encoding='utf-8') as f:
            f.write(content)

# 6. Fix BLE headers for compilation
print("\n6. Fixing BLE headers...")

# Create gatt_structs.h with proper GATT definitions if it doesn't exist
gatt_structs_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "include")
gatt_structs_path = os.path.join(gatt_structs_dir, "gatt_structs.h")
os.makedirs(gatt_structs_dir, exist_ok=True)

if not os.path.exists(gatt_structs_path):
    gatt_structs_h = """/**
 * @file gatt_structs.h
 * @brief GATT structure definitions for STM32WB BLE stack
 */
#pragma once

#include <stdint.h>

/* Attribute Permissions */
#define ATTR_PERMISSION_NONE                   0x00
#define ATTR_PERMISSION_AUTHEN_READ            0x01
#define ATTR_PERMISSION_AUTHEN_WRITE           0x02
#define ATTR_PERMISSION_AUTHOR_READ            0x04
#define ATTR_PERMISSION_AUTHOR_WRITE           0x08
#define ATTR_PERMISSION_ENCRY_READ             0x10
#define ATTR_PERMISSION_ENCRY_WRITE            0x20
#define ATTR_PERMISSION_AUTHEN_SIGNED_WRITE    0x40
#define ATTR_PERMISSION_AUTHEN_SIGNED_READ     0x80

/* GATT Value Length Constants */
#define CHAR_VALUE_LEN_CONSTANT                0x00
#define CHAR_VALUE_LEN_VARIABLE                0x01

/* GATT Event Masks */
#define GATT_DONT_NOTIFY_EVENTS                0x00
#define GATT_NOTIFY_ATTRIBUTE_WRITE            0x01
#define GATT_NOTIFY_WRITE_REQ_AND_WAIT_FOR_APPL_RESP 0x02
#define GATT_NOTIFY_READ_REQ_AND_WAIT_FOR_APPL_RESP  0x04

/* UUID Types */
#define UUID_TYPE_16                           0x01
#define UUID_TYPE_128                          0x02

/* Service Types */
#define PRIMARY_SERVICE                        0x01
#define SECONDARY_SERVICE                      0x02

/* UUID Definitions */
typedef union {
    uint16_t Char_UUID_16;
    uint8_t Char_UUID_128[16];
} Char_UUID_t;

typedef union {
    uint16_t Serv_UUID_16;
    uint8_t Serv_UUID_128[16];
} Service_UUID_t;

/* Characteristic Parameters */
typedef struct {
    uint8_t Properties;
    uint16_t Max_Attribute_Records;
    uint16_t Char_Value_Length;
    uint8_t UUID_Type;
    Char_UUID_t UUID;
    uint8_t Security_Permissions;
    uint8_t GATT_Evt_Mask;
    uint8_t Enc_Key_Size;
    uint8_t Is_Variable;
} BleGattCharacteristicParams;

/* GATT Event Structures */
typedef struct {
    uint16_t Connection_Handle;
    uint16_t Attr_Handle;
    uint8_t Offset;
    uint16_t Attr_Data_Length;
    uint8_t Attr_Data[512];
} aci_gatt_attribute_modified_event_rp0;

typedef struct {
    uint16_t Connection_Handle;
} aci_gatt_server_confirmation_event_rp0;

/* GATT Event Codes */
#define HCI_VENDOR_SPECIFIC_DEBUG_EVT_CODE           0xFF
#define ACI_GATT_ATTRIBUTE_MODIFIED_VSEVT_CODE       0x0C
#define ACI_GATT_SERVER_CONFIRMATION_VSEVT_CODE      0x0D

/* GATT Service Types */
#define PRIMARY_SERVICE               0x01
#define SECONDARY_SERVICE             0x02

/* GATT Attribute Types */
#define CHARACTERISTIC_UUID           0x03
#define INCLUDE_UUID                  0x04

/* GATT function declarations */
tBleStatus aci_gatt_add_serv(uint8_t service_type, uint8_t* uuid, uint8_t service_uuid_type, uint8_t max_attr_records, uint16_t* serviceHandle);
tBleStatus aci_gatt_add_char(uint16_t serviceHandle, uint8_t charUuidType, uint8_t* charUuid, uint16_t charValueLen, uint8_t charProperties, uint8_t secPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* charHandle);
tBleStatus aci_gatt_update_char_value(uint16_t serviceHandle, uint16_t charHandle, uint8_t charValOffset, uint8_t charValueLen, uint8_t* charValue);
tBleStatus aci_gatt_update_char_value_ext(uint16_t conn_handle, uint16_t service_handle, uint16_t char_handle, uint8_t update_type, uint16_t char_length, uint16_t value_offset, uint8_t value_length, uint8_t* value);
tBleStatus aci_gatt_add_char_desc(uint16_t serviceHandle, uint16_t charHandle, uint8_t descUuidType, uint8_t* uuid, uint8_t descValueMaxLen, uint8_t descValueLen, uint8_t* descValue, uint8_t secPermissions, uint8_t accPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* descHandle);
"""

    with open(gatt_structs_path, "w") as f:
        f.write(gatt_structs_h)
    print(f"✓ Created gatt_structs.h with GATT definitions")

# 7. Update ble.h to include gatt_structs.h
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the file if it exists
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    # Add include for gatt_structs.h if not present
    if '#include "include/gatt_structs.h"' not in content:
        content = content.replace(
            "#pragma once",
            "#pragma once\n\n#include \"include/gatt_structs.h\""
        )
        
        with open(ble_h_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✓ Updated ble.h to include gatt_structs.h")

print("\nAll integration steps completed! You can now try building the full firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
