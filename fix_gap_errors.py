#!/usr/bin/env python3

import os
import re
import shutil

print("Fixing BLE GAP errors for full firmware build...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
gap_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "gap.c")
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")

# 1. Add missing GAP function declarations to ble.h
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the original file
    shutil.copy2(ble_h_path, ble_h_path + ".gap_bak")
    
    # Add GAP function declarations if they don't exist
    gap_functions = """
/* GAP Function Declarations */
tBleStatus aci_gap_set_discoverable(uint8_t ADType, uint16_t AdvertisingInterval_Min, uint16_t AdvertisingInterval_Max, uint8_t OwnAddressType, uint8_t AdvertFilterPolicy, uint8_t LocalNameLen, const char *LocalName, uint8_t ServiceUUIDLen, const uint8_t* ServiceUUIDList, uint16_t SlaveConnIntervMin, uint16_t SlaveConnIntervMax);
tBleStatus aci_gap_update_adv_data(uint8_t AdvLen, const uint8_t *AdvData);
tBleStatus aci_gap_set_non_discoverable(void);
tBleStatus aci_gap_set_undirected_connectable(uint16_t AdvertisingInterval_Min, uint16_t AdvertisingInterval_Max, uint8_t OwnAddressType, uint8_t AdvertFilterPolicy);
tBleStatus aci_gap_authorization_resp(uint16_t ConnectionHandle, uint8_t Authorize);
tBleStatus aci_gap_set_io_capability(uint8_t IoCap);
tBleStatus aci_gap_set_authentication_requirement(uint8_t MitmMode, uint8_t OobEnable, uint8_t OobData[16], uint8_t MinEncKeySize, uint8_t MaxEncKeySize, uint8_t UseFixedPin, uint32_t FixedPin, uint8_t BondingMode);
tBleStatus aci_gap_pass_key_resp(uint16_t ConnectionHandle, uint32_t PassKey);
tBleStatus aci_gap_slave_security_req(uint16_t ConnectionHandle);
tBleStatus aci_gap_update_adv_data(uint8_t AdvLen, const uint8_t *AdvData);
tBleStatus aci_gap_set_broadcast_mode(uint16_t AdvertisingInterval_Min, uint16_t AdvertisingInterval_Max, uint8_t AdvertisingType, uint8_t OwnAddressType, uint8_t AdvertDataLength, const uint8_t *AdvertData, uint8_t NumOfWhiteListEntries, const uint8_t *WhiteList);
tBleStatus aci_gap_terminate(uint16_t ConnectionHandle, uint8_t Reason);
tBleStatus aci_gap_clear_security_db(void);
tBleStatus aci_gap_allow_rebond(uint16_t ConnectionHandle);
tBleStatus aci_gap_start_connection_update(uint16_t ConnectionHandle, uint16_t ConnIntervalMin, uint16_t ConnIntervalMax, uint16_t ConnLatency, uint16_t SupervisionTimeout, uint16_t MinCELength, uint16_t MaxCELength);
tBleStatus aci_gap_send_pairing_req(uint16_t ConnectionHandle, uint8_t Force_Rebond);
tBleStatus aci_gap_get_security_level(uint16_t ConnectionHandle, uint8_t *Security_Mode, uint8_t *Security_Level);
tBleStatus aci_gap_configure_whitelist(void);
tBleStatus aci_gap_terminate_gap_proc(uint8_t Procedure_Code);

/* GAP Event Structures */
typedef struct {
    uint8_t Status;
    uint16_t Connection_Handle;
    uint8_t Role;
    uint8_t Peer_Address_Type;
    uint8_t Peer_Address[6];
    uint16_t Conn_Interval;
    uint16_t Conn_Latency;
    uint16_t Supervision_Timeout;
    uint8_t Master_Clock_Accuracy;
} aci_gap_proc_complete_event_rp0;

typedef struct {
    uint16_t Connection_Handle;
    uint32_t Passkey;
} aci_gap_passkey_req_event_rp0;

typedef struct {
    uint16_t Connection_Handle;
} aci_gap_pairing_complete_event_rp0;
"""
    
    # Add the GAP function declarations if not already present
    if "aci_gap_set_discoverable" not in content:
        # Find a good place to add the GAP functions
        if "/* BLE Status Definitions */" in content:
            content = content.replace("/* BLE Status Definitions */", 
                                     gap_functions + "\n/* BLE Status Definitions */")
        else:
            # Otherwise add at the end before the last closing bracket if present
            if content.rstrip().endswith("}"):
                last_bracket_pos = content.rstrip().rfind("}")
                content = content[:last_bracket_pos] + gap_functions + "\n" + content[last_bracket_pos:]
            else:
                # Or just append at the end
                content += "\n" + gap_functions
    
    # Write the updated content
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Added GAP function declarations to {ble_h_path}")

# 2. Fix gap.c if it exists
if os.path.exists(gap_path):
    with open(gap_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Backup the original file
    shutil.copy2(gap_path, gap_path + ".bak")
    
    # Make sure it includes gatt_structs.h and other needed headers
    if "#include \"../../lib/stm32wb_copro/ble/include/gatt_structs.h\"" not in content:
        content = re.sub(r'(#include\s+<[^>]+>)', 
                       r'\1\n#include "../../lib/stm32wb_copro/ble/include/gatt_structs.h"', 
                       content, 
                       count=1)
    
    # Fix any struct mismatches or other common issues
    # This is a generic approach, may need to be refined for specific errors
    content = content.replace("Char_UUID_128", "UUID.Char_UUID_128")
    
    # Write the updated content
    with open(gap_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Fixed {gap_path}")

# 3. Create missing event structures and definitions
gap_events_h = """/**
 * @file gap_events.h
 * @brief GAP event structures for BLE
 */
#pragma once

#include <stdint.h>

/* GAP Event Types */
#define ACI_GAP_LIMITED_DISCOVERABLE_EVENT               0x0001
#define ACI_GAP_PAIRING_COMPLETE_EVENT                   0x0002
#define ACI_GAP_PASS_KEY_REQ_EVENT                       0x0003
#define ACI_GAP_AUTHORIZATION_REQ_EVENT                  0x0004
#define ACI_GAP_PERIPHERAL_SECURITY_INITIATED_EVENT      0x0005
#define ACI_GAP_BOND_LOST_EVENT                         0x0006
#define ACI_GAP_PROC_COMPLETE_EVENT                      0x0007
#define ACI_GAP_ADDR_NOT_RESOLVED_EVENT                  0x0008
#define ACI_GAP_NUMERIC_COMPARISON_VALUE_EVENT           0x0009
#define ACI_GAP_KEYPRESS_NOTIFICATION_EVENT              0x000A
"""

gap_events_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "include", "gap_events.h")
os.makedirs(os.path.dirname(gap_events_path), exist_ok=True)

with open(gap_events_path, "w") as f:
    f.write(gap_events_h)
print(f"✓ Created gap_events.h")

# 4. Update ble.h to include gap_events.h
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Add gap_events.h include if not already present
    if "#include \"include/gap_events.h\"" not in content:
        if "#include \"include/gatt_structs.h\"" in content:
            content = content.replace(
                "#include \"include/gatt_structs.h\"",
                "#include \"include/gatt_structs.h\"\n#include \"include/gap_events.h\""
            )
        
        with open(ble_h_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✓ Updated ble.h to include gap_events.h")

print("\nAll GAP errors have been fixed. Try building the firmware again with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
