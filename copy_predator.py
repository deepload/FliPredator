#!/usr/bin/env python3
import os
import shutil
import sys

def copy_predator_app():
    """Copy predator app to firmware directory"""
    source_dir = "predator_app"
    dest_dir = os.path.join("flipperzero-firmware-wPlugins", "applications_user", "predator")
    
    if not os.path.exists(source_dir):
        print(f"Error: {source_dir} not found")
        return False
    
    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy all files and directories
    try:
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            dest_path = os.path.join(dest_dir, item)
            
            if os.path.isdir(source_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                print(f"Copied directory: {item}")
            else:
                shutil.copy2(source_path, dest_path)
                print(f"Copied file: {item}")
        
        print(f"Successfully copied predator app to {dest_dir}")
        return True
        
    except Exception as e:
        print(f"Error copying files: {e}")
        return False

if __name__ == "__main__":
    success = copy_predator_app()
    sys.exit(0 if success else 1)
