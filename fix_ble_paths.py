#!/usr/bin/env python3

import os
import shutil
import glob

def main():
    print("Fixing BLE include path issues...")

    # Base paths
    firmware_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
    lib_path = os.path.join(firmware_path, "lib", "stm32wb_copro")
    interface_path = os.path.join(lib_path, "interface", "patterns", "ble_thread")
    
    # Create directory structure
    paths = [
        os.path.join(interface_path, "shci"),
        os.path.join(interface_path, "tl"),
        os.path.join(interface_path, "hw"),
        os.path.join(lib_path, "utilities"),
        os.path.join(firmware_path, "targets", "f7", "ble_glue", "services")
    ]
    
    for path in paths:
        os.makedirs(path, exist_ok=True)
        print(f"✓ Ensured directory: {path}")
    
    # 1. Create missing_types.h in ALL required locations
    missing_types_content = """/**
 * @file missing_types.h
 * @brief Missing type definitions for STM32WB BLE stack
 */

#pragma once

#include <stdint.h>

/* FUS GetState Error Codes */
typedef uint8_t SHCI_FUS_GetState_ErrorCode_t;

/* Wireless Firmware Info structure */
typedef struct {
    uint32_t version_major;
    uint32_t version_minor;
    uint32_t version_sub;
    uint32_t memorySize;
    uint32_t infoStack;
} WirelessFwInfo_t;

/* FUS UpdateAuthKey Command Parameter */
typedef struct {
    uint8_t key[8];
} SHCI_C2_FUS_UpdateAuthKey_Cmd_Param_t;

/* FUS StoreUsrKey Command Parameter */
typedef struct {
    uint8_t KeyType;
    uint8_t encrypted;
    uint8_t key[16];
} SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;

/* Key Types */
#define KEYTYPE_MASTER    0x01
#define KEYTYPE_SIMPLE    0x02
#define KEYTYPE_ENCRYPTED 0x03

/* FUS GetVersion Response Parameter */
typedef struct {
    uint32_t fus_version;
    uint32_t wireless_stack_version;
    uint32_t fus_info;
} SHCI_C2_FUS_GetVersion_Rsp_Param_t;

/* DEBUG Init Command Packet */
typedef struct {
    uint8_t payload[20];
} SHCI_C2_DEBUG_Init_Cmd_Packet_t;

/* Traces Configuration */
typedef struct {
    uint32_t TraceFilter;
    uint32_t Reserved1;
    uint32_t Reserved2;
    uint32_t Reserved3;
} SHCI_C2_DEBUG_TracesConfig_t;

/* FLASH EraseActivity Command Parameter */
typedef uint8_t SHCI_C2_FLASH_EraseActivity_Cmd_Param_t;

/* CONCURRENT Mode Parameter */
typedef uint8_t SHCI_C2_CONCURRENT_Mode_Param_t;

/* FLASH StoreData Command Parameter */
typedef struct {
    uint32_t address;
    uint32_t length;
    uint8_t data[128]; // Arbitrary buffer size
} SHCI_C2_FLASH_StoreData_Cmd_Param_t;

/* FLASH EraseData Command Parameter */
typedef struct {
    uint32_t address;
    uint32_t length;
} SHCI_C2_FLASH_EraseData_Cmd_Param_t;

/* FLASH ACTIVITY CONTROL Source */
typedef uint8_t SHCI_C2_SET_FLASH_ACTIVITY_CONTROL_Source_t;

/* SHCI Command Status */
typedef uint8_t SHCI_CmdStatus_t;

/* SHCI HCI IO and TL Interfaces */
typedef struct
{
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tSHciIO;

typedef struct
{
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tHciIO;

typedef struct
{
  uint8_t *p_cmdbuffer;
  void (*StatusNotCallBack)(uint8_t status);
} HCI_TL_HciInitConf_t;

/* Define Flash Activity constants */
#define ERASE_ACTIVITY_ON  0x01
#define ERASE_ACTIVITY_OFF 0x00

/* HCI TL command status */
#define HCI_TL_CmdBusy 0
#define HCI_TL_CmdAvailable 1
typedef uint8_t HCI_TL_CmdStatus_t;
"""

    # Create missing_types.h in multiple locations to ensure it's found
    locations = [
        os.path.join(interface_path, "shci", "missing_types.h"),
        os.path.join(interface_path, "tl", "missing_types.h"),
        os.path.join(lib_path, "missing_types.h")
    ]
    
    for location in locations:
        with open(location, 'w', encoding='utf-8') as f:
            f.write(missing_types_content)
        print(f"✓ Created missing_types.h in {os.path.dirname(location)}")

    # 2. Create fixed shci.h with correct ble.h include path
    shci_h_content = """/**
 * @file shci.h
 * @brief SHCI interface for STM32WB
 */

#pragma once

#include <stdint.h>
#include "missing_types.h"
#include "../../ble/ble.h"

/* Register IO bus message callbacks */
void shci_register_io_bus(tSHciIO* fops);

/* SHCI C2 FUS Commands */
tBleStatus SHCI_C2_FUS_GetState(SHCI_FUS_GetState_ErrorCode_t *p_rsp);
tBleStatus SHCI_C2_FUS_GetVersion(SHCI_C2_FUS_GetVersion_Rsp_Param_t *p_rsp);
tBleStatus SHCI_C2_FUS_UpdateAuthKey(SHCI_C2_FUS_UpdateAuthKey_Cmd_Param_t *p_cmd);
tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t *p_cmd, uint8_t *p_key);
tBleStatus SHCI_C2_FUS_LoadUsrKey(uint8_t slot);
tBleStatus SHCI_C2_FUS_UnloadUsrKey(uint8_t slot);

/* SHCI C2 Flash Commands */
tBleStatus SHCI_C2_FLASH_EraseActivity(SHCI_C2_FLASH_EraseActivity_Cmd_Param_t *p_cmd);
tBleStatus SHCI_C2_FLASH_StoreData(SHCI_C2_FLASH_StoreData_Cmd_Param_t *p_cmd);
tBleStatus SHCI_C2_FLASH_EraseData(SHCI_C2_FLASH_EraseData_Cmd_Param_t *p_cmd);
tBleStatus SHCI_C2_SetFlashActivityControl(SHCI_C2_SET_FLASH_ACTIVITY_CONTROL_Source_t Source);

/* SHCI C2 BLE/DEBUG Commands */
tBleStatus SHCI_C2_BLE_Init(SHCI_C2_Ble_Init_Cmd_Packet_t *p_cmd_packet);
tBleStatus SHCI_C2_DEBUG_Init(SHCI_C2_DEBUG_Init_Cmd_Packet_t *p_cmd_packet);
tBleStatus SHCI_C2_CONCURRENT_SetMode(SHCI_C2_CONCURRENT_Mode_Param_t *p_param);

/* SHCI C2 Config */
tBleStatus SHCI_C2_Config(SHCI_C2_CONFIG_Cmd_Param_t *p_config_param);

/* SHCI Wireless Firmware Info */
tBleStatus SHCI_GetWirelessFwInfo(WirelessFwInfo_t* p_wireless_info);

/* Hardware IPCC functions */
void HW_IPCC_TRACES_Init(void);
void HW_IPCC_TRACES_EvtNot(void);
"""

    # Write fixed shci.h
    with open(os.path.join(interface_path, "shci", "shci.h"), 'w', encoding='utf-8') as f:
        f.write(shci_h_content)
    print("✓ Created fixed shci.h with correct include paths")

    # 3. Create fixed hci_tl.h
    hci_tl_h_content = """/**
 * @file hci_tl.h
 * @brief HCI Transport Layer interface
 */

#pragma once

#include <stdint.h>
#include "missing_types.h"

/* HCI request structure */
typedef struct
{
  uint16_t ogf;
  uint16_t ocf;
  uint32_t event;
  void *cparam;
  uint32_t clen;
  void *rparam;
  uint32_t rlen;
} hci_request;

/* Event Packet */
typedef struct
{
  uint32_t status;
  uint32_t pckt_type;
  uint32_t evt_len;
  uint8_t *evt_payload;
} TL_EvtPacket_t;

/* HCI TL initialization */
void hci_register_io_bus(tHciIO* fops);
int32_t hci_init(void* param);
int32_t hci_user_evt_proc(void);
"""

    # Write fixed hci_tl.h
    with open(os.path.join(interface_path, "tl", "hci_tl.h"), 'w', encoding='utf-8') as f:
        f.write(hci_tl_h_content)
    print("✓ Created fixed hci_tl.h with proper includes")

    # 4. Create hw.h with HW_IPCC_TRACES functions
    hw_h_content = """/**
 * @file hw.h
 * @brief Hardware interface for STM32WB
 */

#pragma once

#include <stdint.h>

void HW_IPCC_Enable(void);
void HW_IPCC_Init(void);
void HW_IPCC_BLE_Init(void);
void HW_IPCC_TRACES_Init(void);
void HW_IPCC_TRACES_EvtNot(void);
"""

    # Write hw.h
    with open(os.path.join(interface_path, "hw", "hw.h"), 'w', encoding='utf-8') as f:
        f.write(hw_h_content)
    print("✓ Created hw.h with proper function declarations")

    # 5. Fix function calls in extra_beacon.c
    extra_beacon_path = os.path.join(firmware_path, "targets", "f7", "ble_glue", "extra_beacon.c")
    if os.path.exists(extra_beacon_path):
        try:
            with open(extra_beacon_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Fix function call to match required parameters
            content = content.replace(
                "aci_gap_additional_beacon_start(\n        adv_interval_min,\n        adv_interval_max,\n        adv_type,\n        own_address_type,\n        p_adv_data,\n        p_adv_data_len",
                "aci_gap_additional_beacon_start(\n        adv_interval_min,\n        adv_interval_max,\n        adv_type,\n        own_address_type,\n        p_adv_data,\n        p_adv_data_len,\n        0, /* num_whitelist_entries */\n        NULL /* whitelist */"
            )
            
            with open(extra_beacon_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("✓ Fixed extra_beacon.c function arguments")
        except Exception as e:
            print(f"✗ Failed to fix extra_beacon.c: {e}")

    # 6. Fix function calls in serial_service.c
    serial_service_path = os.path.join(firmware_path, "targets", "f7", "ble_glue", "services", "serial_service.c")
    if os.path.exists(serial_service_path):
        try:
            with open(serial_service_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Fix function call to match declaration
            content = content.replace(
                "aci_gatt_update_char_value_ext(\n            service_handle, char_handle,\n            update_type, char_length, value_offset,\n            value_len,",
                "aci_gatt_update_char_value_ext(\n            service_handle, char_handle,\n            update_type, char_length, value_offset,\n            value_len, (const uint8_t*)"
            )
            
            with open(serial_service_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("✓ Fixed serial_service.c function call")
        except Exception as e:
            print(f"✗ Failed to fix serial_service.c: {e}")

    # 7. Create ble.h stub if needed (only if original doesn't exist)
    ble_h_path = os.path.join(lib_path, "ble", "ble.h")
    os.makedirs(os.path.dirname(ble_h_path), exist_ok=True)
    
    if not os.path.exists(ble_h_path):
        ble_h_stub = """/**
 * @file ble.h
 * @brief BLE interface stub
 */

#pragma once

#include <stdint.h>

typedef uint8_t tBleStatus;

/* SHCI_C2_CONFIG command parameter */
typedef struct
{
  uint8_t  *p_ble_buffer_address;
  uint32_t  ble_buffer_size;
  uint8_t   num_attr_records;
  uint8_t   num_attr_serv;
  uint8_t   attr_value_arr_size;
  uint8_t   num_of_links;
  uint8_t   extended_packet_length_enable;
  uint8_t   pr_write_list_size;
  uint8_t   mblock_count;
  uint16_t  att_mtu;
  uint16_t  slave_sca;
  uint16_t  master_sca;
  uint8_t   ls_source;
  uint32_t  max_conn_event_length;
  uint16_t  hs_startup_time;
  uint8_t   viterbi_enable;
  uint8_t   ll_only;
  uint32_t  hw_version;
} SHCI_C2_CONFIG_Cmd_Param_t;

/* SHCI_C2_BLE_Init command packet */
typedef struct
{
  uint8_t   buf[0];
} SHCI_C2_Ble_Init_Cmd_Packet_t;

/* BLE function declarations */
tBleStatus aci_gatt_update_char_value_ext(uint16_t service_handle, uint16_t char_handle, uint8_t update_type, uint16_t char_length, uint16_t value_offset, uint8_t value_length, const uint8_t* value);
tBleStatus aci_gap_additional_beacon_start(uint16_t adv_interval_min, uint16_t adv_interval_max, uint8_t adv_type, uint8_t own_address_type, const uint8_t* adv_data, uint8_t adv_data_length, uint8_t num_whitelist_entries, const uint8_t* whitelist);

/* BLE configuration */
#define CFG_SC_SUPPORT 1
#define CFG_ENCRYPTION_KEY_SIZE_MIN 8
#define CFG_ENCRYPTION_KEY_SIZE_MAX 16
#define CFG_IDENTITY_ADDRESS 0
"""
        
        with open(ble_h_path, 'w', encoding='utf-8') as f:
            f.write(ble_h_stub)
        print("✓ Created ble.h stub with required definitions")

    print("\n✅ All BLE path issues fixed! Try building the firmware now.")

if __name__ == "__main__":
    main()
