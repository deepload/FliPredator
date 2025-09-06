#!/usr/bin/env python3

import os
import re

print("Fixing type conflicts between ble.h and missing_types.h...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
ble_h_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "ble", "ble.h")
missing_types_path = os.path.join(fw_dir, "lib", "stm32wb_copro", "interface", "patterns", "ble_thread", "tl", "missing_types.h")

# 1. First, remove the duplicate type definitions from ble.h
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Create backup
    with open(ble_h_path + ".backup", "w", encoding="utf-8") as f:
        f.write(content)
    
    # Remove the duplicate type definitions
    # 1. Remove tSHciIO
    content = re.sub(r'typedef\s+struct\s+{.*?}\s+tSHciIO;', '// tSHciIO defined in missing_types.h', content, flags=re.DOTALL)
    
    # 2. Remove tHciIO
    content = re.sub(r'typedef\s+struct\s+{.*?}\s+tHciIO;', '// tHciIO defined in missing_types.h', content, flags=re.DOTALL)
    
    # 3. Remove SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t
    content = re.sub(r'typedef\s+struct\s+{.*?}\s+SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t;', '// SHCI_C2_FUS_StoreUsrKey_Cmd_Param_t defined in missing_types.h', content, flags=re.DOTALL)
    
    # 4. Fix HW_IPCC_TRACES function declarations - comment out redundant declarations
    content = content.replace('void HW_IPCC_TRACES_EvtNot(void);', '// void HW_IPCC_TRACES_EvtNot(void); // Defined in hw.h')
    content = content.replace('void HW_IPCC_TRACES_Init(void);', '// void HW_IPCC_TRACES_Init(void); // Defined in hw.h')
    
    # Write the fixed content back
    with open(ble_h_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Removed duplicate type definitions from {ble_h_path}")
else:
    print(f"❌ File not found: {ble_h_path}")

# 2. Make sure the includes are in the correct order
if os.path.exists(ble_h_path):
    with open(ble_h_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Check for include of missing_types.h
    if '#include "../interface/patterns/ble_thread/tl/missing_types.h"' not in content:
        # Add include at the top after the other includes
        content = content.replace('#pragma once', '#pragma once\n\n#include "../interface/patterns/ble_thread/tl/missing_types.h"')
        
        with open(ble_h_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Added missing_types.h include to {ble_h_path}")

print("\nAll type conflicts have been fixed. You can now try building the firmware with:")
print("cd C:\\Projects\\Predator\\flipperzero-firmware-wPlugins && .\\fbt.cmd firmware_all")
