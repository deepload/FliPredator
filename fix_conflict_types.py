import os
import shutil

# Paths
fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_h_path = os.path.join(fw_dir, "lib/stm32wb_copro/ble/ble.h")
missing_types_h_path = os.path.join(fw_dir, "lib/stm32wb_copro/interface/patterns/ble_thread/tl/missing_types.h")

# First remove duplicate types from ble.h
if os.path.exists(ble_h_path):
    with open(ble_h_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Create backup
    shutil.copy2(ble_h_path, ble_h_path + ".bak")
    
    # Remove conflicting definitions
    if "typedef struct _SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;" in content:
        content = content.replace(
            "typedef struct _SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;",
            "// Forward declaration\n// typedef struct _SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;"
        )
        
    if "} tSHciIO;" in content:
        content = content.replace(
            "} tSHciIO;",
            "} tSHciIO_reserved;"
        )
        
    if "} tHciIO;" in content:
        content = content.replace(
            "} tHciIO;",
            "} tHciIO_reserved;"
        )
        
    if "} HCI_TL_HciInitConf_t;" in content:
        content = content.replace(
            "} HCI_TL_HciInitConf_t;",
            "} HCI_TL_HciInitConf_t_reserved;"
        )
        
    if "#define HCI_TL_CmdBusy" in content:
        content = content.replace(
            "#define HCI_TL_CmdBusy",
            "// #define HCI_TL_CmdBusy"
        )

    # Write fixed content
    with open(ble_h_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Removed conflicting type definitions from {ble_h_path}")

# Now fix missing_types.h if it exists
if os.path.exists(missing_types_h_path):
    with open(missing_types_h_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Create backup
    shutil.copy2(missing_types_h_path, missing_types_h_path + ".bak")
    
    # Fix HCI_TL_CmdBusy definition
    content = content.replace(
        "#define HCI_TL_CmdBusy 0",
        "#define HCI_TL_CmdBusy 0x01"
    )
    
    with open(missing_types_h_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Fixed HCI_TL_CmdBusy definition in {missing_types_h_path}")

print("All conflicting BLE type definitions have been fixed!")
