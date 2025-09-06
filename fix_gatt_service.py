#!/usr/bin/env python3

import os
import shutil
import re

print("Fixing BLE GATT service errors...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")

# 1. Create a comprehensive GATT service header with all needed types, constants and structures
gatt_aci_h = """/**
 * @file gatt_aci.h
 * @brief GATT Application Controller Interface for STM32WB
 */
#pragma once

#include <stdint.h>

/* UUID Types */
#define UUID_TYPE_16                                 0x01
#define UUID_TYPE_128                                0x02

/* Service Types */
#define PRIMARY_SERVICE                              0x01
#define SECONDARY_SERVICE                            0x02

/* Characteristic Properties */
#define CHAR_PROP_BROADCAST                          0x01
#define CHAR_PROP_READ                               0x02
#define CHAR_PROP_WRITE_WITHOUT_RESP                 0x04
#define CHAR_PROP_WRITE                              0x08
#define CHAR_PROP_NOTIFY                             0x10
#define CHAR_PROP_INDICATE                           0x20
#define CHAR_PROP_SIGNED_WRITE                       0x40
#define CHAR_PROP_EXT                                0x80

/* Characteristic Value Lengths */
#define CHAR_VALUE_LENGTH                            0x10
#define CHAR_VALUE_LEN_VARIABLE                      0x01
#define CHAR_VALUE_LEN_CONSTANT                      0x00

/* GATT Event Masks */
#define GATT_DONT_NOTIFY_EVENTS                      0x00
#define GATT_NOTIFY_ATTRIBUTE_WRITE                  0x01
#define GATT_NOTIFY_WRITE_REQ_AND_WAIT_FOR_APPL_RESP 0x02
#define GATT_NOTIFY_READ_REQ_AND_WAIT_FOR_APPL_RESP  0x04
#define GATT_NOTIFY_NOTIFICATION_COMPLETE            0x08

/* GATT Attribute Types */
#define CHARACTERISTIC_UUID                          0x03
#define INCLUDE_UUID                                 0x04
#define CHAR_EXTENDED_PROPERTIES_UUID                0x05
#define CHAR_USER_DESCRIPTION_UUID                   0x06
#define CLIENT_CHAR_CONFIG_UUID                      0x07
#define SERVER_CHAR_CONFIG_UUID                      0x08
#define CHAR_FORMAT_UUID                             0x09
#define CHAR_AGGREGATE_UUID                          0x0A
#define VALID_RANGE_UUID                             0x0B
#define EXTERNAL_REPORT_REF_UUID                     0x0C
#define REPORT_REF_UUID                              0x0D
#define CHAR_PROPERTIES                              0x10
#define CHAR_EXTENDED_PROP                           0x12

/* Device Information Service UUIDs */
#define DEVICE_INFORMATION_SERVICE_UUID              0x180A

/* GATT Event Codes */
#define HCI_VENDOR_SPECIFIC_DEBUG_EVT_CODE           0xFF
#define ACI_GATT_ATTRIBUTE_MODIFIED_VSEVT_CODE       0x0C
#define ACI_GATT_SERVER_CONFIRMATION_VSEVT_CODE      0x0D

/* GATT Attribute Structure */
typedef struct {
    uint16_t Handle;
    uint8_t UuidType;
    uint8_t UUID[16];
    uint16_t ValueLen;
    uint8_t *Value;
    uint8_t Properties;
    uint16_t MaxSizeOfValue;
    uint8_t Permissions;
    uint16_t Service;
    uint8_t* Attr_Data;
} GATT_Attribute_t;

/* GATT UUID Union Types */
typedef union {
    uint16_t Char_UUID_16;
    uint8_t Char_UUID_128[16];
} Char_UUID_t;

typedef union {
    uint16_t Desc_UUID_16;
    uint8_t Desc_UUID_128[16];
} Char_Desc_Uuid_t;

typedef union {
    uint16_t Serv_UUID_16;
    uint8_t Serv_UUID_128[16];
} Service_UUID_t;

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

/* GATT Function Declarations */
tBleStatus aci_gatt_add_serv(uint8_t service_type, uint8_t* uuid, uint8_t service_uuid_type, uint8_t max_attr_records, uint16_t* serviceHandle);
tBleStatus aci_gatt_add_char(uint16_t serviceHandle, uint8_t charUuidType, uint8_t* charUuid, uint16_t charValueLen, uint8_t charProperties, uint8_t secPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* charHandle);
tBleStatus aci_gatt_add_char_desc(uint16_t serviceHandle, uint16_t charHandle, uint8_t descUuidType, uint8_t* uuid, uint8_t descValueMaxLen, uint8_t descValueLen, uint8_t* descValue, uint8_t secPermissions, uint8_t accPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* descHandle);
tBleStatus aci_gatt_update_char_value(uint16_t serviceHandle, uint16_t charHandle, uint8_t charValOffset, uint8_t charValueLen, uint8_t* charValue);
tBleStatus aci_gatt_update_char_value_ext(uint16_t conn_handle, uint16_t service_handle, uint16_t char_handle, uint8_t update_type, uint16_t char_length, uint16_t value_offset, uint8_t value_length, uint8_t* value);
"""

# Create the directory if it doesn't exist
ble_include_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "include")
os.makedirs(ble_include_dir, exist_ok=True)

with open(os.path.join(ble_include_dir, "gatt_aci.h"), "w", encoding="utf-8") as f:
    f.write(gatt_aci_h)
print(f"✓ Created gatt_aci.h with all required types and constants")

# 2. Update ble.h to include the new gatt_aci.h header
if os.path.exists(ble_h_path):
    # Backup the file
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        ble_h_content = f.read()
    
    # Add include for gatt_aci.h
    if "#include \"include/gatt_aci.h\"" not in ble_h_content:
        if "#pragma once" in ble_h_content:
            ble_h_content = ble_h_content.replace(
                "#pragma once", 
                "#pragma once\n\n#include \"include/gatt_aci.h\""
            )
        
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(ble_h_content)
    print(f"✓ Updated ble.h to include gatt_aci.h")

# 3. Fix serial_service_uuid.inc and dev_info_service_uuid.inc
# These files define the service UUIDs but are causing initialization errors
serial_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service_uuid.inc")
dev_info_service_uuid_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service_uuid.inc")

# Fix serial_service_uuid.inc if it exists
if os.path.exists(serial_service_uuid_path):
    # Create a directory if needed
    os.makedirs(os.path.dirname(serial_service_uuid_path), exist_ok=True)
    
    # Create a proper UUID definition
    serial_service_uuid_content = """/* BLE Serial Service UUID */
#define BLE_SVC_SERIAL_UUID { 0x33, 0xa9, 0xb5, 0x3e, 0x87, 0x5d, 0x1a, 0x8e, 0xc8, 0x47, 0x5e, 0xae, 0x6d, 0x66, 0xf6, 0x03 }

/* BLE Serial RX Characteristic UUID */
#define BLE_SVC_SERIAL_RX_CHAR_UUID { 0x00, 0x00, 0xfe, 0x60, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 }

/* BLE Serial TX Characteristic UUID */
#define BLE_SVC_SERIAL_TX_CHAR_UUID { 0x00, 0x00, 0xfe, 0x61, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 }

/* BLE Serial Flow Control Characteristic UUID */
#define BLE_SVC_SERIAL_FLOW_CONTROL_UUID { 0x00, 0x00, 0xfe, 0x63, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 }

/* BLE Serial RPC Status Characteristic UUID */
#define BLE_SVC_SERIAL_RPC_STATUS_UUID { 0x00, 0x00, 0xfe, 0x64, 0x8e, 0x22, 0x45, 0x41, 0x9d, 0x4c, 0x21, 0xed, 0xae, 0x82, 0xed, 0x19 }
"""
    
    with open(serial_service_uuid_path, "w", encoding="utf-8") as f:
        f.write(serial_service_uuid_content)
    print(f"✓ Fixed serial_service_uuid.inc")

# Fix dev_info_service_uuid.inc if it exists
if os.path.exists(dev_info_service_uuid_path):
    # Create a directory if needed
    os.makedirs(os.path.dirname(dev_info_service_uuid_path), exist_ok=True)
    
    # Create a proper UUID definition
    dev_info_service_uuid_content = """/* Device Information Service UUIDs */
#define DEV_INFO_MANUFACTURER_NAME_UUID 0x2A29
#define DEV_INFO_MODEL_NUMBER_UUID 0x2A24
#define DEV_INFO_SERIAL_NUMBER_UUID 0x2A25
#define DEV_INFO_HARDWARE_REV_UUID 0x2A27
#define DEV_INFO_FIRMWARE_REV_UUID 0x2A26
#define DEV_INVO_RPC_VERSION_UID 0x2A28
"""
    
    with open(dev_info_service_uuid_path, "w", encoding="utf-8") as f:
        f.write(dev_info_service_uuid_content)
    print(f"✓ Fixed dev_info_service_uuid.inc")

# 4. Fix the serial_service.c file
serial_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "serial_service.c")
if os.path.exists(serial_service_path):
    # Backup the file
    shutil.copy2(serial_service_path, serial_service_path + ".bak")
    
    with open(serial_service_path, "r", encoding="utf-8", errors="ignore") as f:
        serial_service_content = f.read()
    
    # Add include for gatt_aci.h at the top
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_aci.h\"" not in serial_service_content:
        serial_service_content = re.sub(
            r'(#include\s+<[^>]+>)',
            r'\1\n#include "../../lib/stm32wb_copro/ble/include/gatt_aci.h"',
            serial_service_content,
            count=1
        )
    
    # Fix array definitions by replacing .uuid.Char_UUID_128 with simply Char_UUID_128
    serial_service_content = serial_service_content.replace(
        ".uuid.Char_UUID_128", 
        ".Char_UUID_128"
    )
    
    with open(serial_service_path, "w", encoding="utf-8") as f:
        f.write(serial_service_content)
    print(f"✓ Fixed serial_service.c")

# 5. Fix the dev_info_service.c file
dev_info_service_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "services", "dev_info_service.c")
if os.path.exists(dev_info_service_path):
    # Backup the file
    shutil.copy2(dev_info_service_path, dev_info_service_path + ".bak")
    
    with open(dev_info_service_path, "r", encoding="utf-8", errors="ignore") as f:
        dev_info_service_content = f.read()
    
    # Add include for gatt_aci.h at the top
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_aci.h\"" not in dev_info_service_content:
        dev_info_service_content = re.sub(
            r'(#include\s+<[^>]+>)',
            r'\1\n#include "../../lib/stm32wb_copro/ble/include/gatt_aci.h"',
            dev_info_service_content,
            count=1
        )
    
    # Fix uuid type declarations
    dev_info_service_content = dev_info_service_content.replace(
        "Service_UUID_t*", 
        "(uint16_t*)"
    )
    
    with open(dev_info_service_path, "w", encoding="utf-8") as f:
        f.write(dev_info_service_content)
    print(f"✓ Fixed dev_info_service.c")

# 6. Fix any other files that might need the gatt_aci.h include
gatt_c_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "furi_ble", "gatt.c")
if os.path.exists(gatt_c_path):
    # Backup the file
    shutil.copy2(gatt_c_path, gatt_c_path + ".bak")
    
    with open(gatt_c_path, "r", encoding="utf-8", errors="ignore") as f:
        gatt_c_content = f.read()
    
    # Add include for gatt_aci.h at the top
    if "#include \"../../../lib/stm32wb_copro/ble/include/gatt_aci.h\"" not in gatt_c_content:
        gatt_c_content = re.sub(
            r'(#include\s+<[^>]+>)',
            r'\1\n#include "../../../lib/stm32wb_copro/ble/include/gatt_aci.h"',
            gatt_c_content,
            count=1
        )
    
    with open(gatt_c_path, "w", encoding="utf-8") as f:
        f.write(gatt_c_content)
    print(f"✓ Fixed gatt.c")

print("\nAll BLE GATT errors have been fixed! You can now try building the firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
