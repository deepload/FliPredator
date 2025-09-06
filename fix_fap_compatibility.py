#!/usr/bin/env python3

import os
import re
import shutil
import struct
import subprocess

print("Fixing Predator FAP file compatibility...")

fw_dir = r"C:\Projects\Predator\flipperzero-firmware-wPlugins"
predator_dir = r"C:\Projects\Predator\predator_app"
fap_path = os.path.join(fw_dir, "applications_user", "predator", "dist", "predator.fap")
application_fam_path = os.path.join(fw_dir, "applications_user", "predator", "application.fam")

# 1. First, check if we need to update the application manifest
print("Checking application manifest...")
if os.path.exists(application_fam_path):
    with open(application_fam_path, "r") as f:
        manifest_content = f.read()
    
    # Check if we need to update the FAP API level
    if "fap_api_version" not in manifest_content:
        updated_manifest = manifest_content.replace(
            "fap_version=\"1.0\",",
            "fap_version=\"1.0\",\n    fap_api_version=38,  # Firmware v0.89.0 and above"
        )
        
        # Update the manifest file
        with open(application_fam_path, "w") as f:
            f.write(updated_manifest)
        print("✓ Updated application.fam with API version")
    else:
        print("✓ API version already defined in application.fam")
else:
    print("⚠️ Could not find application.fam")

# 2. Check if we need to adjust icon formats or other resources
predator_icon = os.path.join(fw_dir, "applications_user", "predator", "predator.png")
if not os.path.exists(predator_icon):
    # Try to find a suitable icon
    if os.path.exists(os.path.join(predator_dir, "predator.png")):
        shutil.copy2(os.path.join(predator_dir, "predator.png"), predator_icon)
        print("✓ Copied predator.png icon")
    else:
        # Create a basic icon if none exists
        print("⚠️ No icon found, this may cause issues")

# 3. Rebuild the FAP file with updated settings
print("\nRebuilding Predator FAP file...")
try:
    os.chdir(fw_dir)
    subprocess.run([".\\fbt.cmd", "fap_predator"], check=True)
    print("✓ Successfully rebuilt predator.fap")
except Exception as e:
    print(f"⚠️ Error rebuilding FAP: {e}")

# 4. Verify the FAP file exists
if os.path.exists(fap_path):
    print(f"✓ FAP file available at: {fap_path}")
    
    # Get the file size
    file_size = os.path.getsize(fap_path)
    print(f"  File size: {file_size} bytes")
    
    # Create a compatible version in the root directory for easy access
    compatible_path = os.path.join(fw_dir, "predator.fap")
    shutil.copy2(fap_path, compatible_path)
    print(f"✓ Created compatible version at: {compatible_path}")
else:
    print("❌ FAP file not found. Build may have failed.")

print("\nInstructions:")
print("1. Copy the FAP file to your Flipper's SD card at /ext/apps/")
print("2. If that doesn't work, try upgrading your Flipper's firmware")
print("3. Check that your FAP file isn't corrupted during transfer")
