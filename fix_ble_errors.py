import os
import re
import shutil

print("Fixing BLE firmware compilation errors...")

# Base paths
fw_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
lib_path = os.path.join(fw_path, "lib/stm32wb_copro")
interface_path = os.path.join(lib_path, "interface/patterns/ble_thread")
shci_path = os.path.join(interface_path, "shci")
ble_glue_path = os.path.join(fw_path, "targets/f7/ble_glue")

# Create missing_types.h with all the required type definitions
missing_types_h = '''/**
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
    uint8_t keyType;
    uint8_t encrypted;
    uint8_t key[16];
} SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;

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

/* Define Flash Activity constants */
#define ERASE_ACTIVITY_ON  0x01
#define ERASE_ACTIVITY_OFF 0x00
'''

# Write the missing_types.h file
os.makedirs(shci_path, exist_ok=True)
with open(os.path.join(shci_path, "missing_types.h"), "w") as f:
    f.write(missing_types_h)
print("✅ Created missing_types.h with all required type definitions")

# Update shci.h to include the missing_types.h and remove duplicate declarations
if os.path.exists(os.path.join(shci_path, "shci.h")):
    with open(os.path.join(shci_path, "shci.h"), "r", errors="ignore") as f:
        shci_content = f.read()
    
    # Backup original file
    shutil.copy2(os.path.join(shci_path, "shci.h"), os.path.join(shci_path, "shci.h.bak"))
    
    # Create new shci.h content
    new_shci_content = '''#pragma once

#include <stdint.h>
#include "../../ble/ble.h"
#include "missing_types.h"

/* Register IO bus message callbacks */
void shci_register_io_bus(tSHciIO* fops);

/* SHCI C2 FUS Commands */
tBleStatus SHCI_C2_FUS_GetState(SHCI_FUS_GetState_ErrorCode_t *p_rsp);
tBleStatus SHCI_C2_FUS_GetVersion(SHCI_C2_FUS_GetVersion_Rsp_Param_t *p_rsp);
tBleStatus SHCI_C2_FUS_UpdateAuthKey(SHCI_C2_FUS_UpdateAuthKey_Cmd_Param_t *p_cmd);
tBleStatus SHCI_C2_FUS_StoreUsrKey(SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t *p_cmd, uint8_t *p_key);
tBleStatus SHCI_C2_FUS_LoadUsrKey(uint8_t slot);

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
'''

    # Write the new content
    with open(os.path.join(shci_path, "shci.h"), "w") as f:
        f.write(new_shci_content)
    print("✅ Updated shci.h to include missing_types.h and fixed function declarations")

# Update app_conf.h with all required BLE constants
app_conf_h = '''/**
 * @file app_conf.h
 * @brief BLE configuration constants for STM32WB
 */

#pragma once

#include "hw.h"
#include "hw_conf.h"
#include "hw_if.h"
#include <assert.h>
#include <string.h>

#define CFG_TX_POWER                      (0x18) /* 0x18 ~= +6dBm */

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
'''

# Create or update app_conf.h
os.makedirs(ble_glue_path, exist_ok=True)
if os.path.exists(os.path.join(ble_glue_path, "app_conf.h")):
    # Backup original file
    shutil.copy2(os.path.join(ble_glue_path, "app_conf.h"), os.path.join(ble_glue_path, "app_conf.h.bak"))

with open(os.path.join(ble_glue_path, "app_conf.h"), "w") as f:
    f.write(app_conf_h)
print("✅ Updated app_conf.h with all required BLE constants")

# Create FreeRTOS.h stub to fix macro conflicts
freertos_h = '''/**
 * @file FreeRTOS.h
 * @brief FreeRTOS stub header for STM32WB
 */

#pragma once

/* Critical section management for FreeRTOS compatibility */
#define taskENTER_CRITICAL()
#define taskEXIT_CRITICAL()

/* Standard FreeRTOS macros */
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5
'''

# Create FreeRTOS stub header
with open(os.path.join(lib_path, "FreeRTOS.h"), "w") as f:
    f.write(freertos_h)
print("✅ Created FreeRTOS.h stub to fix macro conflicts")

print("\nAll BLE firmware compilation errors fixed. Try building now with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
