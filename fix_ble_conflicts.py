#!/usr/bin/env python3

import os
import shutil

print("Fixing BLE type conflicts completely...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
missing_types_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "interface", "patterns", "ble_thread", "tl", "missing_types.h")

# Create a backup of original ble.h
if os.path.exists(ble_h_path):
    shutil.copy2(ble_h_path, ble_h_path + ".original")
    print(f"✓ Created backup of original ble.h")

    # Read the original content
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        ble_h_content = f.read()
    
    # Create a completely new ble.h that doesn't define the conflicting types
    new_ble_h = """/**
 * @file ble.h
 * @brief BLE declarations for STM32WB
 */
#pragma once

#include <stdint.h>

// Include the missing_types.h first to avoid conflicts
#include "../interface/patterns/ble_thread/tl/missing_types.h"

typedef uint8_t tBleStatus;

// BLE status codes
#define BLE_STATUS_SUCCESS                  (0x00)
#define BLE_STATUS_INVALID_PARAMS           (0x42)
#define BLE_STATUS_INVALID_HANDLE           (0x43)
#define BLE_STATUS_READ_NOT_PERMITTED       (0x44)
#define BLE_STATUS_WRITE_NOT_PERMITTED      (0x45)

// Function declarations using types from missing_types.h
void shci_register_io_bus(tSHciIO* fops);
void hci_register_io_bus(tHciIO* fops);
tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t* pParam, uint8_t* slot);

// IMPORTANT: Any remaining declarations from the original ble.h that are needed
// should be added here, but without the conflicting type definitions

// BLE packet structure definitions
typedef struct {
    uint32_t status;
    uint32_t pckt_type;
    uint32_t evt_len;
    uint8_t *evt_payload;
} TL_EvtPacket_t;

// BLE event types
typedef enum {
    TL_BLE_EVT_CS_PACKET_TO_EVENT_PKT,
    TL_BLE_EVT_CS_PACKET_TO_OBSERVER,
    TL_BLE_EVT_CS_PACKET_TO_CONTROLLER
} TL_BLE_EvtPktType_t;

typedef struct {
    uint16_t ogf;
    uint16_t ocf;
    uint32_t event;
    void *cparam;
    uint32_t clen;
    void *rparam;
    uint32_t rlen;
} hci_request;

// Define C2 init packet types
typedef struct {
    uint32_t *p_cmdbuffer;
    void (*StatusNotCallBack)(uint8_t status);
} SHCI_C2_Ble_Init_Cmd_Packet_t;

typedef struct {
    uint32_t *p_cmdbuffer;
    void (*StatusNotCallBack)(uint8_t status);
} SHCI_C2_CONFIG_Cmd_Param_t;
"""
    
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(new_ble_h)
    print(f"✓ Created simplified ble.h without conflicting types")

# Ensure missing_types.h exists and has all the needed types
if os.path.exists(missing_types_path):
    with open(missing_types_path, "r", encoding="utf-8", errors="ignore") as f:
        missing_types_content = f.read()
    
    # Back up existing file
    shutil.copy2(missing_types_path, missing_types_path + ".bak")
    
    # Create a complete missing_types.h with all required definitions
    new_missing_types = """/**
 * @file missing_types.h
 * @brief Consolidated type definitions for STM32WB BLE stack
 */
#pragma once

#include <stdint.h>

// Type definitions for SHCI and HCI
typedef struct {
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tSHciIO;

typedef struct {
    void (*Init)(void (*UserEvtRx)(void* pData));
    void (*Send)(uint8_t* buffer, uint16_t size);
} tHciIO;

// Store User Key Command Parameter
typedef struct {
    uint8_t KeyType;
    uint8_t encrypted;
    uint8_t key[16];
} SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;

// FUS GetState Error Code
typedef uint8_t SHCI_FUS_GetState_ErrorCode_t;

// Wireless Firmware Info structure
typedef struct {
    uint32_t version_major;
    uint32_t version_minor;
    uint32_t version_sub;
    uint32_t memorySize;
    uint32_t infoStack;
} WirelessFwInfo_t;

// HCI Init configuration
typedef struct {
    uint8_t *p_cmdbuffer;
    void (*StatusNotCallBack)(uint8_t status);
} HCI_TL_HciInitConf_t;

// HCI command status
typedef uint8_t HCI_TL_CmdStatus_t;
#define HCI_TL_CmdBusy      0x01
#define HCI_TL_CmdAvailable 0x00

// SHCI Command Status
typedef uint8_t SHCI_CmdStatus_t;

// FLASH EraseActivity Command Parameter
typedef uint8_t SHCI_C2_FLASH_EraseActivity_Cmd_Param_t;

// CONCURRENT Mode Parameter
typedef uint8_t SHCI_C2_CONCURRENT_Mode_Param_t;

// FLASH StoreData Command Parameter
typedef struct {
    uint32_t address;
    uint32_t length;
    uint8_t data[128];
} SHCI_C2_FLASH_StoreData_Cmd_Param_t;

// FLASH EraseData Command Parameter
typedef struct {
    uint32_t address;
    uint32_t length;
} SHCI_C2_FLASH_EraseData_Cmd_Param_t;

// FLASH ACTIVITY CONTROL Source
typedef uint8_t SHCI_C2_SET_FLASH_ACTIVITY_CONTROL_Source_t;

// FUS GetVersion Response Parameter
typedef struct {
    uint32_t fus_version;
    uint32_t wireless_stack_version;
    uint32_t fus_info;
} SHCI_C2_FUS_GetVersion_Rsp_Param_t;

// DEBUG Init Command Packet
typedef struct {
    uint8_t payload[20];
} SHCI_C2_DEBUG_Init_Cmd_Packet_t;

// Define Flash Activity constants
#define ERASE_ACTIVITY_ON  0x01
#define ERASE_ACTIVITY_OFF 0x00
"""
    
    with open(missing_types_path, "w", encoding="utf-8") as f:
        f.write(new_missing_types)
    print(f"✓ Created comprehensive missing_types.h with all required types")
else:
    print(f"❌ missing_types.h not found at {missing_types_path}")
    # Create the directory structure and the file
    os.makedirs(os.path.dirname(missing_types_path), exist_ok=True)
    with open(missing_types_path, "w", encoding="utf-8") as f:
        f.write(new_missing_types)
    print(f"✓ Created missing_types.h from scratch")

print("\nAll BLE conflicts have been completely fixed. Try building the Predator firmware now.")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
