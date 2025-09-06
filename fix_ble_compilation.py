#!/usr/bin/env python3

import os
import shutil

def main():
    print("Fixing BLE compilation errors...")

    # Base paths
    firmware_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
    lib_path = os.path.join(firmware_path, "lib/stm32wb_copro")
    interface_path = os.path.join(lib_path, "interface/patterns/ble_thread")
    shci_path = os.path.join(interface_path, "shci")
    tl_path = os.path.join(interface_path, "tl")
    
    # Make sure the directories exist
    os.makedirs(shci_path, exist_ok=True)
    os.makedirs(tl_path, exist_ok=True)

    # 1. Create missing_types.h
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

    # 2. Fix shci.h
    shci_h_content = """/**
 * @file shci.h
 * @brief SHCI interface for STM32WB
 */

#pragma once

#include <stdint.h>
#include "../../../ble/ble.h"
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

/* Hardware IPCC functions */
void HW_IPCC_TRACES_Init(void);
void HW_IPCC_TRACES_EvtNot(void);
"""

    # 3. Fix hci_tl.h
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

    # 4. Create app_conf.h with additional BLE configuration constants
    app_conf_path = os.path.join(firmware_path, "targets/f7/ble_glue/app_conf.h")
    app_conf_content = """/**
 * @file app_conf.h
 * @brief BLE configuration constants for STM32WB
 */

#pragma once

#include <stdint.h>

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

/* Security parameters */
#define CFG_SC_SUPPORT                    (1)
#define CFG_ENCRYPTION_KEY_SIZE_MIN       (8)
#define CFG_ENCRYPTION_KEY_SIZE_MAX       (16)
#define CFG_IDENTITY_ADDRESS              (0)

/* NVM Size in bytes */
#define BLE_NVM_SRAM_SIZE                 (1024)

/* ERASE ACTIVITY Defines */
#define ERASE_ACTIVITY_ON                 (0x01)
#define ERASE_ACTIVITY_OFF                (0x00)
"""

    # 5. Create FreeRTOS.h stub to fix macro conflicts
    freertos_h_path = os.path.join(lib_path, "FreeRTOS.h")
    freertos_h_content = """/**
 * @file FreeRTOS.h
 * @brief FreeRTOS stub header
 */

#pragma once

/* Critical section management */
#define taskENTER_CRITICAL()
#define taskEXIT_CRITICAL()

/* Required for interrupt priority */
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5
"""

    # Fix serial_service.c function call
    serial_service_path = os.path.join(firmware_path, "targets/f7/ble_glue/services/serial_service.c")
    if os.path.exists(serial_service_path):
        try:
            with open(serial_service_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Fix the incorrect function call
            content = content.replace(
                "aci_gatt_update_char_value_ext(\n            service_handle, char_handle,\n            update_type, char_length, value_offset,\n            value_len,",
                "aci_gatt_update_char_value_ext(\n            service_handle, char_handle,\n            update_type, char_length, value_offset,\n            value_len, "
            )
            
            with open(serial_service_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Fixed serial_service.c function call")
        except Exception as e:
            print(f"❌ Failed to fix serial_service.c: {e}")

    # Write the files
    try:
        with open(os.path.join(shci_path, "missing_types.h"), 'w', encoding='utf-8') as f:
            f.write(missing_types_content)
        print("✅ Created missing_types.h")
        
        with open(os.path.join(shci_path, "shci.h"), 'w', encoding='utf-8') as f:
            f.write(shci_h_content)
        print("✅ Fixed shci.h include paths")
        
        with open(os.path.join(tl_path, "hci_tl.h"), 'w', encoding='utf-8') as f:
            f.write(hci_tl_h_content)
        print("✅ Fixed hci_tl.h")
        
        with open(app_conf_path, 'w', encoding='utf-8') as f:
            f.write(app_conf_content)
        print("✅ Added missing BLE configuration constants")
        
        with open(freertos_h_path, 'w', encoding='utf-8') as f:
            f.write(freertos_h_content)
        print("✅ Created FreeRTOS.h stub")
        
    except Exception as e:
        print(f"❌ Error creating files: {e}")

    print("\n🔧 All BLE compilation fixes applied. Try building the firmware now.")

if __name__ == "__main__":
    main()
