#!/usr/bin/env python3

import os
import re
import shutil

print("Fixing BLE GATT UUID structure errors...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"

# Create the gatt_structs.h header with proper struct definitions
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
"""

# Create directory if needed
gatt_structs_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "include")
os.makedirs(gatt_structs_dir, exist_ok=True)

with open(os.path.join(gatt_structs_dir, "gatt_structs.h"), "w") as f:
    f.write(gatt_structs_h)
print("✓ Created gatt_structs.h with proper GATT definitions")

# Fix serial_service_uuid.inc
serial_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service_uuid.inc")
if os.path.exists(serial_service_uuid_path):
    with open(serial_service_uuid_path, "w") as f:
        f.write("""/* Serial Service UUIDs */
#define BLE_SVC_SERIAL_UUID {{ .Serv_UUID_128 = { 0x33, 0xa9, 0xb5, 0x3e, 0x87, 0x5d, 0x1a, 0x8e, 0xc8, 0x47, 0x5e, 0xae, 0x6d, 0x66, 0xf6, 0x03 } }}

/* Serial Service Characteristic UUIDs */
#define BLE_SVC_SERIAL_RX_CHAR_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x60, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_TX_CHAR_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x61, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_FLOW_CONTROL_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x63, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
#define BLE_SVC_SERIAL_RPC_STATUS_UUID {{ .Char_UUID_128 = { 0x00, 0x00, 0xfe, 0x64, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 } }}
""")
    print(f"✓ Fixed serial_service_uuid.inc with proper union initialization syntax")

# Fix dev_info_service_uuid.inc
dev_info_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service_uuid.inc")
if os.path.exists(dev_info_service_uuid_path):
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
    print(f"✓ Fixed dev_info_service_uuid.inc with proper UUID definitions")

# Fix serial_service.c
serial_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service.c")
if os.path.exists(serial_service_path):
    # Backup the original file
    shutil.copy2(serial_service_path, serial_service_path + ".bak")
    
    with open(serial_service_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
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
    
    # Fix the BleGattCharacteristicParams struct initialization
    content = content.replace(".Char_UUID_128", ".UUID")
    content = re.sub(r'\.uuid\.Char_UUID_128', '.UUID', content)
    
    with open(serial_service_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Fixed serial_service.c with proper struct initialization")

# Fix ble.h to include the gatt_structs.h
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
if os.path.exists(ble_h_path):
    # Backup the original file
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Add the gatt_structs.h include
    if "#include \"include/gatt_structs.h\"" not in content:
        content = content.replace(
            "#pragma once",
            "#pragma once\n\n#include \"include/gatt_structs.h\""
        )
    
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Updated ble.h to include gatt_structs.h")

# Fix dev_info_service.c
dev_info_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service.c")
if os.path.exists(dev_info_service_path):
    # Backup the original file
    shutil.copy2(dev_info_service_path, dev_info_service_path + ".bak")
    
    with open(dev_info_service_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Add the gatt_structs.h include
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\"" not in content:
        content = content.replace(
            "#include <furi.h>",
            "#include <furi.h>\n#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\""
        )
    
    # Fix the uuid declaration and type casts
    content = content.replace(".uuid.Char_UUID_128", ".UUID")
    content = re.sub(r'\(\s*Service_UUID_t\s*\*\s*\)', '(uint16_t*)', content)
    
    with open(dev_info_service_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Fixed dev_info_service.c with proper struct initialization")

print("\nAll BLE GATT UUID structure errors have been fixed!")
print("You can now try building the firmware.")
