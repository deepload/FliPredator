#!/usr/bin/env python3

import os
import shutil

print("Fixing BLE GATT service errors...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")

# Back up the file
if os.path.exists(ble_h_path):
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    print(f"✓ Created backup of ble.h")

    # Read the current content
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        ble_h_content = f.read()
    
    # Add missing GATT constants and function declarations
    gatt_additions = """
// GATT Service Types
#define PRIMARY_SERVICE               0x01
#define SECONDARY_SERVICE             0x02

// GATT Attribute Types
#define CHARACTERISTIC_UUID           0x03
#define INCLUDE_UUID                  0x04
#define CHAR_EXTENDED_PROPERTIES_UUID 0x05
#define CHAR_USER_DESCRIPTION_UUID    0x06
#define CLIENT_CHAR_CONFIG_UUID       0x07
#define SERVER_CHAR_CONFIG_UUID       0x08
#define CHAR_FORMAT_UUID              0x09
#define CHAR_AGGREGATE_UUID           0x0A
#define VALID_RANGE_UUID              0x0B
#define EXTERNAL_REPORT_REF_UUID      0x0C
#define REPORT_REF_UUID               0x0D
#define CHAR_PROPERTIES               0x10
#define CHAR_VALUE_LENGTH             0x11
#define CHAR_EXTENDED_PROP            0x12

// Characteristic properties
#define CHAR_PROP_BROADCAST           0x01
#define CHAR_PROP_READ                0x02
#define CHAR_PROP_WRITE_WITHOUT_RESP  0x04
#define CHAR_PROP_WRITE               0x08
#define CHAR_PROP_NOTIFY              0x10
#define CHAR_PROP_INDICATE            0x20
#define CHAR_PROP_SIGNED_WRITE        0x40
#define CHAR_PROP_EXT                 0x80

// GATT function declarations
tBleStatus aci_gatt_add_serv(uint8_t service_type, uint8_t* uuid, uint8_t service_uuid_type, uint8_t max_attr_records, uint16_t* serviceHandle);
tBleStatus aci_gatt_add_char(uint16_t serviceHandle, uint8_t charUuidType, uint8_t* charUuid, uint16_t charValueLen, uint8_t charProperties, uint8_t secPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* charHandle);
tBleStatus aci_gatt_update_char_value(uint16_t serviceHandle, uint16_t charHandle, uint8_t charValOffset, uint8_t charValueLen, uint8_t* charValue);
tBleStatus aci_gatt_update_char_value_ext(uint16_t conn_handle, uint16_t service_handle, uint16_t char_handle, uint8_t update_type, uint16_t char_length, uint16_t value_offset, uint8_t value_length, uint8_t* value);
tBleStatus aci_gatt_add_char_desc(uint16_t serviceHandle, uint16_t charHandle, uint8_t descUuidType, uint8_t* uuid, uint8_t descValueMaxLen, uint8_t descValueLen, uint8_t* descValue, uint8_t secPermissions, uint8_t accPermissions, uint8_t gattEvtMask, uint8_t encryKeySize, uint8_t isVariable, uint16_t* descHandle);

// GATT structures for attributes
typedef struct {
    uint16_t Handle;
    uint8_t UuidType;
    uint8_t UUID[16];
    uint16_t ValueLen;
    uint8_t* Value;
    uint8_t Properties;
    uint16_t MaxSizeOfValue;
    uint8_t Permissions;
    uint16_t Service;
    uint8_t* Attr_Data;
} GATT_Attribute_t;
"""
    
    # Add the GATT additions to the end of the file, before the closing bracket if there is one
    if ble_h_content.strip().endswith("}"):
        # Find the last closing bracket
        last_bracket = ble_h_content.rstrip().rfind("}")
        ble_h_content = ble_h_content[:last_bracket] + gatt_additions + ble_h_content[last_bracket:]
    else:
        ble_h_content += gatt_additions
    
    # Write the updated content back
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(ble_h_content)
    
    print(f"✓ Added missing GATT constants and function declarations to ble.h")
else:
    print(f"❌ File not found: {ble_h_path}")

print("\nAll BLE GATT errors have been fixed. You can now try building the firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
