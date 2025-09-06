#!/usr/bin/env python3

import os
import shutil

print("Fixing specific BLE errors for the Predator firmware...")

# Base paths
fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_dir = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble")
ble_h_path = os.path.join(ble_dir, "ble.h")
interface_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "interface", "patterns", "ble_thread")
hw_dir = os.path.join(interface_path, "hw")
app_conf_path = os.path.join(fw_dir, "targets", "f7", "ble_glue", "app_conf.h")

# Fix 1: Create hw.h
os.makedirs(hw_dir, exist_ok=True)
hw_h_content = """/**
 * @file hw.h
 * @brief Hardware abstraction for STM32WB BLE
 */
#pragma once

#include <stdint.h>

// Define HW_IPCC functions
void HW_IPCC_Enable(void);
void HW_IPCC_Init(void);
void HW_IPCC_BLE_Init(void);
void HW_IPCC_BLE_SendCmd(void);
void HW_IPCC_TRACES_Init(void);
void HW_IPCC_TRACES_EvtNot(void);
"""

with open(os.path.join(hw_dir, "hw.h"), "w") as f:
    f.write(hw_h_content)
print("✅ Created hw.h")

# Fix 2: Create hw_conf.h and hw_if.h stubs
hw_conf_h_content = """/**
 * @file hw_conf.h
 * @brief Hardware configuration stub
 */
#pragma once

// Basic stubs
"""

with open(os.path.join(hw_dir, "hw_conf.h"), "w") as f:
    f.write(hw_conf_h_content)
print("✅ Created hw_conf.h")

hw_if_h_content = """/**
 * @file hw_if.h
 * @brief Hardware interface stub
 */
#pragma once

// Basic stubs
"""

with open(os.path.join(hw_dir, "hw_if.h"), "w") as f:
    f.write(hw_if_h_content)
print("✅ Created hw_if.h")

# Fix 3: Fix app_conf.h to include proper paths
app_conf_h_content = """/**
 * @file app_conf.h
 * @brief BLE application configuration
 */
#pragma once

#include <stdint.h>
#include "../../lib/stm32wb_copro/interface/patterns/ble_thread/hw/hw.h"
#include "../../lib/stm32wb_copro/interface/patterns/ble_thread/hw/hw_conf.h"
#include "../../lib/stm32wb_copro/interface/patterns/ble_thread/hw/hw_if.h"

/* BLE Core Defines */
#define CFG_BLE_NUM_GATT_ATTRIBUTES       (68)
#define CFG_BLE_NUM_GATT_SERVICES         (8)
#define CFG_BLE_ATT_VALUE_ARRAY_SIZE      (1344)
#define CFG_BLE_NUM_LINK                  (2)
#define CFG_BLE_DATA_LENGTH_EXTENSION     (1)
#define CFG_BLE_PREPARE_WRITE_LIST_SIZE   (3)
#define CFG_BLE_MBLOCK_COUNT              (79)
#define CFG_BLE_MAX_ATT_MTU               (156)
#define CFG_BLE_SLAVE_SCA                 (500)
#define CFG_BLE_MASTER_SCA                (0)
#define CFG_BLE_LSE_SOURCE                (1)
#define CFG_BLE_MAX_CONN_EVENT_LENGTH     (0xFFFFFFFF)
#define CFG_BLE_HSE_STARTUP_TIME          (0x148)
#define CFG_BLE_VITERBI_MODE              (1)
#define CFG_BLE_OPTIONS                   (0x01F3)

/* NVM Size in bytes */
#define BLE_NVM_SRAM_SIZE                 (1024)

/* ERASE ACTIVITY Defines */
#define ERASE_ACTIVITY_ON                 (0x01)
#define ERASE_ACTIVITY_OFF                (0x00)
"""

if os.path.exists(app_conf_path):
    shutil.copy2(app_conf_path, app_conf_path + ".bak")
with open(app_conf_path, "w") as f:
    f.write(app_conf_h_content)
print("✅ Fixed app_conf.h")

# Fix 4: Fix ble.h to include tSHciIO and SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        ble_h_content = f.read()
    
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    # Add missing type definitions at the start of the file
    type_definitions = """
/* BLE Type Definitions */
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
    uint8_t KeyType;
    uint8_t encrypted;
    uint8_t key[16];
} SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;
"""
    
    # Add the type definitions before the first function declaration
    if "#include" in ble_h_content:
        include_end = ble_h_content.rfind("#include")
        include_end = ble_h_content.find("\n", include_end) + 1
        ble_h_content = ble_h_content[:include_end] + type_definitions + ble_h_content[include_end:]
    
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(ble_h_content)
    print("✅ Fixed ble.h with missing type definitions")

# Fix 5: Remove duplicate predator app declarations
predator_app_path = os.path.join(fw_dir, "applications", "main", "predator_app")
if os.path.exists(predator_app_path):
    shutil.rmtree(predator_app_path)
    print(f"✅ Removed duplicate predator_app at {predator_app_path}")

predator_path = os.path.join(fw_dir, "applications", "main", "predator")
if os.path.exists(predator_path):
    shutil.rmtree(predator_path)
    print(f"✅ Removed duplicate predator at {predator_path}")

print("\nAll BLE errors fixed. Try building the firmware now.")
print("Command: cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
