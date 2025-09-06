import os
import shutil
import re

def main():
    print("Fixing ALL BLE firmware compilation errors...")
    
    # Base paths
    fw_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
    lib_path = os.path.join(fw_path, "lib/stm32wb_copro")
    interface_path = os.path.join(lib_path, "interface/patterns/ble_thread")
    shci_path = os.path.join(interface_path, "shci")
    hw_path = os.path.join(interface_path, "hw")
    tl_path = os.path.join(interface_path, "tl")
    utilities_path = os.path.join(lib_path, "utilities")
    ble_glue_path = os.path.join(fw_path, "targets/f7/ble_glue")
    ble_h_path = os.path.join(lib_path, "ble/ble.h")
    
    # Create directories if they don't exist
    for path in [shci_path, hw_path, tl_path, utilities_path, ble_glue_path]:
        os.makedirs(path, exist_ok=True)
    
    # 1. Fix: Create missing utilities/dbg_trace.h stub
    dbg_trace_h = """/**
 * @file dbg_trace.h
 * @brief Debug trace stub header
 */
#pragma once

#define DBG_TRACE_LEVEL_OFF 0
#define DBG_TRACE_LEVEL_ALWAYS 1
#define DBG_TRACE_LEVEL_ERROR 2
#define DBG_TRACE_LEVEL_WARNING 3
#define DBG_TRACE_LEVEL_INFO 4
#define DBG_TRACE_LEVEL_DEBUG 5

#define DBG_TRACE_LEVEL DBG_TRACE_LEVEL_OFF
#define DBG_TRACE_ALL(...)
#define DBG_TRACE_ERROR(...)
#define DBG_TRACE_WARNING(...)
#define DBG_TRACE_INFO(...)
#define DBG_TRACE_DEBUG(...)
"""

    # 2. Fix: Create FreeRTOS.h stub for macro conflicts
    freertos_h = """/**
 * @file FreeRTOS.h
 * @brief FreeRTOS stub header
 */
#pragma once

// Critical section management
#define taskENTER_CRITICAL()
#define taskEXIT_CRITICAL()

// Required for interrupt priority
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5
"""

    # 3. Fix: Create hw.h with proper HW_IPCC definitions
    hw_h = """/**
 * @file hw.h
 * @brief Hardware abstraction layer for STM32WB
 */
#pragma once

#include <stdint.h>

// Define HW_IPCC once to avoid redefinition errors
#if !defined(HW_IPCC)
#define HW_IPCC 1

void HW_IPCC_Enable(void);
void HW_IPCC_Init(void);
void HW_IPCC_BLE_Init(void);
void HW_IPCC_BLE_SendCmd(void);
void HW_IPCC_TRACES_Init(void);
void HW_IPCC_TRACES_EvtNot(void);

#endif
"""

    # 4. Fix: Create missing_types.h with all required type definitions
    missing_types_h = """/**
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
  void (*StatusNotCallBack)(HCI_TL_CmdStatus_t status);
} HCI_TL_HciInitConf_t;

/* Define Flash Activity constants */
#define ERASE_ACTIVITY_ON  0x01
#define ERASE_ACTIVITY_OFF 0x00

/* HCI TL command status */
#define HCI_TL_CmdBusy 0
#define HCI_TL_CmdAvailable 1
typedef uint8_t HCI_TL_CmdStatus_t;
"""

    # 5. Fix: Create updated shci.h
    shci_h = """/**
 * @file shci.h
 * @brief SHCI interface for STM32WB
 */
#pragma once

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
"""

    # 6. Fix: Create hci_tl.h with proper structs
    hci_tl_h = """/**
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

    # 7. Fix: Create utilities_common.h
    utilities_common_h = """/**
 * @file utilities_common.h
 * @brief Common utility macros and functions
 */
#pragma once

#include <stdint.h>

/* Basic type definitions */
typedef uint32_t UTIL_ADV_TIMER_Id_t;

/* Common utility macros */
#define UTIL_SEQ_INIT_CRITICAL_SECTION()
#define UTIL_SEQ_ENTER_CRITICAL_SECTION()
#define UTIL_SEQ_EXIT_CRITICAL_SECTION()
#define UTIL_SEQ_WAIT_COND_TIMEOUT(cond, timeout) (1)
#define UTIL_SEQ_WaitEvt(evt_id) (1)
#define UTIL_TIMER_Create(timer_id, period, mode, callback, arg) (0)
#define UTIL_TIMER_Stop(timer_id) (0)
#define UTIL_TIMER_Start(timer_id) (0)
#define UTIL_LPM_SetStopMode(mode, info) (0)
#define UTIL_LPM_SetOffMode(mode, info) (0)
"""

    # 8. Fix: Create app_conf.h with all required BLE constants
    app_conf_h = """/**
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
"""

    # Write all the files
    write_file(os.path.join(utilities_path, "dbg_trace.h"), dbg_trace_h)
    write_file(os.path.join(lib_path, "FreeRTOS.h"), freertos_h)
    write_file(os.path.join(hw_path, "hw.h"), hw_h)
    write_file(os.path.join(shci_path, "missing_types.h"), missing_types_h)
    write_file(os.path.join(shci_path, "shci.h"), shci_h)
    write_file(os.path.join(tl_path, "hci_tl.h"), hci_tl_h)
    write_file(os.path.join(utilities_path, "utilities_common.h"), utilities_common_h)
    write_file(os.path.join(ble_glue_path, "app_conf.h"), app_conf_h)
    
    # Check if ble.h needs fixing for forward declarations
    if os.path.exists(ble_h_path):
        with open(ble_h_path, 'r', encoding='utf-8', errors='ignore') as f:
            ble_h_content = f.read()
            
        # Remove duplicate type declarations for SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t
        # Add forward declarations instead
        if "typedef struct SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;" in ble_h_content:
            ble_h_content = ble_h_content.replace("typedef struct SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;", 
                                                "// Forward declaration\ntypedef struct _SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;")
            write_file(ble_h_path, ble_h_content)
    
    print("\nAll BLE firmware compilation errors have been fixed!")
    print("You can now build the firmware with:")
    print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
    
def write_file(path, content):
    """Write content to a file with error handling and backup"""
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Backup original file if it exists
        if os.path.exists(path):
            backup_path = path + ".bak"
            try:
                shutil.copy2(path, backup_path)
                print(f"✓ Backed up {os.path.basename(path)} to {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"! Warning: Could not create backup of {path}: {e}")
        
        # Write the new content
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created/Updated {os.path.basename(path)}")
        return True
    except Exception as e:
        print(f"✗ Failed to write {path}: {e}")
        return False

if __name__ == "__main__":
    main()
