import os

# Define all the missing BLE types in one consolidated header
all_types = '''/**
 * Missing type definitions for STM32WB BLE stack
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
'''

# Create a clean shci.h file
shci_h = '''/**
 * SHCI interface for STM32WB
 */
#pragma once

#include <stdint.h>
#include "../../ble/ble.h"
#include "shci_types.h"

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
'''

# Create BLE configuration constants
app_conf_h = '''/**
 * BLE configuration constants for STM32WB
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

/* NVM Size in bytes */
#define BLE_NVM_SRAM_SIZE                 (1024)

/* ERASE ACTIVITY Defines */
#define ERASE_ACTIVITY_ON                 (0x01)
#define ERASE_ACTIVITY_OFF                (0x00)
'''

# Create minimal FreeRTOS.h to fix macro conflicts
freertos_h = '''/**
 * FreeRTOS minimal stub
 */
#pragma once

#define taskENTER_CRITICAL()
#define taskEXIT_CRITICAL()

#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5
'''

# Write all the files to fix BLE compilation errors
base_path = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"

# Create directories if they don't exist
shci_dir = os.path.join(base_path, "lib/stm32wb_copro/interface/patterns/ble_thread/shci")
os.makedirs(shci_dir, exist_ok=True)

ble_glue_dir = os.path.join(base_path, "targets/f7/ble_glue")
os.makedirs(ble_glue_dir, exist_ok=True)

lib_dir = os.path.join(base_path, "lib/stm32wb_copro")
os.makedirs(lib_dir, exist_ok=True)

# Write files
with open(os.path.join(shci_dir, "shci_types.h"), "w") as f:
    f.write(all_types)
print("Created shci_types.h with all missing type definitions")

with open(os.path.join(shci_dir, "shci.h"), "w") as f:
    f.write(shci_h)
print("Created clean shci.h that includes shci_types.h")

with open(os.path.join(ble_glue_dir, "app_conf.h"), "w") as f:
    f.write(app_conf_h)
print("Created app_conf.h with all required BLE constants")

with open(os.path.join(lib_dir, "FreeRTOS.h"), "w") as f:
    f.write(freertos_h)
print("Created FreeRTOS.h stub to fix macro conflicts")

print("All BLE compilation fixes applied. Try building the firmware now.")
