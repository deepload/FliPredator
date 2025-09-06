#!/usr/bin/env python3

import os
import shutil
import glob
import re

print("Comprehensive Predator Firmware Fix Script")
print("=========================================")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
predator_dir = r"C:\Projects\Predator\predator_app"

# Step 1: Fix duplicate app declarations
print("\n1. Fixing duplicate app declarations...")

# Remove duplicate predator directories if they exist
for path in [
    os.path.join(fw_dir, "applications", "main", "predator"),
    os.path.join(fw_dir, "applications", "main", "predator_app")
]:
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✓ Removed duplicate app at {path}")
        except Exception as e:
            print(f"✗ Failed to remove {path}: {e}")

# Step 2: Create proper application.fam in applications_user/predator
print("\n2. Creating proper application.fam...")
user_predator_dir = os.path.join(fw_dir, "applications_user", "predator")
os.makedirs(user_predator_dir, exist_ok=True)

application_fam = """App(
    appid="predator",
    name="Predator",
    apptype=FlipperAppType.EXTERNAL,
    entry_point="predator_app",
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
    stack_size=4 * 1024,
    order=10,
    fap_icon="predator.png",
    fap_category="Tools",
    fap_author="Predator Team",
    fap_version="1.0",
    fap_description="Advanced penetration testing toolkit for Flipper Zero with Predator module",
)
"""

with open(os.path.join(user_predator_dir, "application.fam"), "w") as f:
    f.write(application_fam)
print("✓ Created application.fam in applications_user/predator")

# Step 3: Fix BLE GATT structures and UUIDs
print("\n3. Fixing BLE GATT structures...")

# Create gatt_structs.h with proper GATT definitions
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
"""

gatt_structs_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "include")
os.makedirs(gatt_structs_dir, exist_ok=True)

with open(os.path.join(gatt_structs_dir, "gatt_structs.h"), "w") as f:
    f.write(gatt_structs_h)
print("✓ Created gatt_structs.h with proper GATT definitions")

# Fix serial_service_uuid.inc
serial_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service_uuid.inc")
os.makedirs(os.path.dirname(serial_service_uuid_path), exist_ok=True)

with open(serial_service_uuid_path, "w") as f:
    f.write("""/* Serial Service UUIDs */
#define BLE_SVC_SERIAL_UUID {{ .Serv_UUID_128 = { 0x33, 0xa9, 0xb5, 0x3e, 0x87, 0x5d, 0x1a, 0x8e, 0xc8, 0x47, 0x5e, 0xae, 0x6d, 0x66, 0xf6, 0x03 } }}

/* Serial Service Characteristic UUIDs */
#define BLE_SVC_SERIAL_RX_CHAR_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x60, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_TX_CHAR_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x61, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_FLOW_CONTROL_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x63, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_RPC_STATUS_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x64, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
""")
print("✓ Fixed serial_service_uuid.inc")

# Fix dev_info_service_uuid.inc
dev_info_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service_uuid.inc")
os.makedirs(os.path.dirname(dev_info_service_uuid_path), exist_ok=True)

with open(dev_info_service_uuid_path, "w") as f:
    f.write("""/* Device Information Service UUIDs */
#define DEVICE_INFORMATION_SERVICE_UUID 0x180A
#define MANUFACTURER_NAME_UUID 0x2A29
#define MODEL_NUMBER_UUID 0x2A24
#define SERIAL_NUMBER_UUID 0x2A25
#define HARDWARE_REVISION_UUID 0x2A27
#define FIRMWARE_REVISION_UUID 0x2A26
#define SOFTWARE_REVISION_UUID 0x2A28
#define DEV_INVO_RPC_VERSION_UID 0x2A28
""")
print("✓ Fixed dev_info_service_uuid.inc")

# Step 4: Update ble.h to include gatt_structs.h
print("\n4. Updating ble.h...")
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the original file
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    # Add the gatt_structs.h include if not already present
    if "#include \"include/gatt_structs.h\"" not in content:
        content = content.replace(
            "#pragma once",
            "#pragma once\n\n#include \"include/gatt_structs.h\""
        )
        
        with open(ble_h_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✓ Updated ble.h to include gatt_structs.h")
    else:
        print("✓ ble.h already includes gatt_structs.h")

# Step 5: Fix BLE service implementations
print("\n5. Fixing BLE service implementations...")

# Fix serial_service.c
serial_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service.c")
if os.path.exists(serial_service_path):
    with open(serial_service_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the original file
    shutil.copy2(serial_service_path, serial_service_path + ".bak")
    
    # Add the gatt_structs.h include
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\"" not in content:
        content = content.replace(
            "#include <furi.h>",
            "#include <furi.h>\n#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\""
        )
    
    # Fix the service_uuid declaration in ble_svc_serial_start function
    content = re.sub(
        r'ble_gatt_service_add\(\s*UUID_TYPE_128,\s*&service_uuid,',
        'Service_UUID_t service_uuid = BLE_SVC_SERIAL_UUID;\n    ble_gatt_service_add(UUID_TYPE_128, &service_uuid,',
        content
    )
    
    # Fix struct member references
    content = content.replace(".Char_UUID_128", ".UUID")
    content = re.sub(r'\.uuid\.Char_UUID_128', '.UUID', content)
    
    with open(serial_service_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ Fixed serial_service.c")

# Fix dev_info_service.c
dev_info_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service.c")
if os.path.exists(dev_info_service_path):
    with open(dev_info_service_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the original file
    shutil.copy2(dev_info_service_path, dev_info_service_path + ".bak")
    
    # Add the gatt_structs.h include
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\"" not in content:
        content = content.replace(
            "#include <furi.h>",
            "#include <furi.h>\n#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\""
        )
    
    # Fix struct member references and type casts
    content = content.replace(".uuid.Char_UUID_128", ".UUID")
    content = re.sub(r'\(\s*Service_UUID_t\s*\*\s*\)', '(uint16_t*)', content)
    
    with open(dev_info_service_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ Fixed dev_info_service.c")

# Step 6: Fix scene includes
print("\n6. Fixing scene includes...")
scene_dir = os.path.join(fw_dir, "applications_user", "predator", "scenes")
os.makedirs(scene_dir, exist_ok=True)

# Copy scene files from predator_app to applications_user/predator if needed
if not os.path.exists(os.path.join(scene_dir, "predator_scene.h")) and os.path.exists(os.path.join(predator_dir, "scenes", "predator_scene.h")):
    for scene_file in glob.glob(os.path.join(predator_dir, "scenes", "*.*")):
        shutil.copy2(scene_file, scene_dir)
    print("✓ Copied scene files to applications_user/predator/scenes")

# Fix includes in scene files
for scene_file in glob.glob(os.path.join(scene_dir, "predator_scene_*.c")):
    with open(scene_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add scene.h include if not present
    if '#include "predator_scene.h"' not in content:
        modified = content.replace('#include "../predator_i.h"', '#include "../predator_i.h"\n#include "predator_scene.h"')
        
        with open(scene_file, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        print(f"✓ Added scene header include to {os.path.basename(scene_file)}")

# Step 7: Fix predator UART initialization
print("\n7. Fixing predator UART initialization...")

# Copy predator.c and other necessary files if they don't exist
predator_c_path = os.path.join(fw_dir, "applications_user", "predator", "predator.c")
if not os.path.exists(predator_c_path) and os.path.exists(os.path.join(predator_dir, "predator.c")):
    shutil.copy2(os.path.join(predator_dir, "predator.c"), predator_c_path)
    print(f"✓ Copied predator.c to applications_user/predator")

# Copy helper files if they don't exist
helpers_dir = os.path.join(fw_dir, "applications_user", "predator", "helpers")
os.makedirs(helpers_dir, exist_ok=True)
if os.path.exists(os.path.join(predator_dir, "helpers")):
    for helper_file in glob.glob(os.path.join(predator_dir, "helpers", "*.*")):
        shutil.copy2(helper_file, helpers_dir)
    print(f"✓ Copied helper files to applications_user/predator/helpers")

# Copy UART files if they don't exist
predator_uart_h_path = os.path.join(fw_dir, "applications_user", "predator", "predator_uart.h")
predator_uart_c_path = os.path.join(fw_dir, "applications_user", "predator", "predator_uart.c")
if not os.path.exists(predator_uart_h_path) and os.path.exists(os.path.join(predator_dir, "predator_uart.h")):
    shutil.copy2(os.path.join(predator_dir, "predator_uart.h"), predator_uart_h_path)
    print(f"✓ Copied predator_uart.h")

if not os.path.exists(predator_uart_c_path) and os.path.exists(os.path.join(predator_dir, "predator_uart.c")):
    shutil.copy2(os.path.join(predator_dir, "predator_uart.c"), predator_uart_c_path)
    print(f"✓ Copied predator_uart.c")

# Fix predator.c UART initialization if needed
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

# Step 8: Copy icon if needed
print("\n8. Copying application icon...")
icon_path = os.path.join(fw_dir, "applications_user", "predator", "predator.png")
if not os.path.exists(icon_path) and os.path.exists(os.path.join(predator_dir, "predator.png")):
    shutil.copy2(os.path.join(predator_dir, "predator.png"), icon_path)
    print("✓ Copied predator.png")

# Final output
print("\nAll fixes have been applied! You can now try building the firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
print("or just the Predator app with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd fap_predator")
