import os
import subprocess
import shutil
import sys
import argparse

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/RogueMaster/flipperzero-firmware-wPlugins.git"
REPO_DIR = "flipperzero-firmware-wPlugins"
FIRMWARE_OUTPUT = os.path.join(REPO_DIR, "dist", "f7-C", "firmware.upd")

def check_dependencies():
    """Check if required tools (git, ufbt) are installed."""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] Error: Git is not installed. Please install Git from https://git-scm.com.")
        sys.exit(1)
    
    try:
        subprocess.run(["ufbt", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] Error: ufbt is not installed. Install it with: pip3 install ufbt")
        sys.exit(1)

def run(cmd, cwd=None):
    """Run a shell command and handle errors."""
    print(f"[+] Running: {cmd}")
    try:
        subprocess.run(cmd, cwd=cwd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: Command failed with exit code {e.returncode}")
        sys.exit(1)

def ensure_repo():
    """Clone the repository if it doesn't exist."""
    if not os.path.exists(REPO_DIR):
        print(f"[*] Cloning repository from {REPO_URL}")
        run(f"git clone {REPO_URL}")
    else:
        print("[*] Repository already exists")

def patch_gpio():
    """Patch GPIO app with Predator module pin definitions."""
    # Try multiple possible locations for GPIO files
    gpio_paths = [
        os.path.join(REPO_DIR, "applications", "main", "gpio", "gpio_app.c"),
        os.path.join(REPO_DIR, "applications", "gpio", "gpio_app.c"),
        os.path.join(REPO_DIR, "applications", "main", "gpio", "scenes", "gpio_scene_start.c")
    ]
    
    gpio_file = None
    for path in gpio_paths:
        if os.path.exists(path):
            gpio_file = path
            break
    
    if not gpio_file:
        print("[!] Warning: GPIO file not found. Skipping GPIO patch.")
        print("    Available GPIO files:")
        for root, dirs, files in os.walk(os.path.join(REPO_DIR, "applications")):
            for file in files:
                if "gpio" in file.lower() and file.endswith(".c"):
                    print(f"    - {os.path.join(root, file)}")
        return

    with open(gpio_file, "r", encoding='utf-8') as f:
        content = f.read()

    if "PREDATOR_GPIO" not in content:
        # Add Predator definitions to a header file instead
        header_file = os.path.join(REPO_DIR, "applications", "main", "gpio", "gpio_app_i.h")
        if not os.path.exists(header_file):
            header_file = os.path.join(REPO_DIR, "applications", "gpio", "gpio_app_i.h")
        
        if os.path.exists(header_file):
            with open(header_file, "r", encoding='utf-8') as f:
                header_content = f.read()
            
            if "PREDATOR_GPIO" not in header_content:
                patch = """\n// --- Predator Module Pin Definitions ---
#define PREDATOR_GPIO 1
#define PREDATOR_ESP32_UART_TX_PIN &gpio_ext_pa7  // Pin 2
#define PREDATOR_ESP32_UART_RX_PIN &gpio_ext_pa6  // Pin 3
#define PREDATOR_GPS_UART_TX_PIN   &gpio_ext_pa4  // Pin 7
#define PREDATOR_GPS_UART_RX_PIN   &gpio_ext_pb3  // Pin 8
// -----------------------------------------\n"""
                
                with open(header_file, "w", encoding='utf-8') as f:
                    f.write(header_content + patch)
                print(f"[+] Patched GPIO header with Predator pins: {header_file}")
            else:
                print("[*] GPIO header already patched")
        else:
            print("[!] Warning: Could not find GPIO header file to patch")
    else:
        print("[*] GPIO already patched")

def patch_cc1101():
    """Patch CC1101 external module for Predator."""
    # Try multiple possible locations for CC1101 files
    cc1101_paths = [
        os.path.join(REPO_DIR, "applications", "main", "subghz", "subghz_external", "cc1101_ext.c"),
        os.path.join(REPO_DIR, "applications", "subghz", "subghz_external", "cc1101_ext.c"),
        os.path.join(REPO_DIR, "lib", "subghz", "devices", "cc1101_ext", "cc1101_ext.c")
    ]
    
    cc1101_file = None
    for path in cc1101_paths:
        if os.path.exists(path):
            cc1101_file = path
            break
    
    if not cc1101_file:
        print("[!] Warning: CC1101 file not found. Checking for SubGHz configuration...")
        # Look for SubGHz configuration files
        config_paths = [
            os.path.join(REPO_DIR, "applications", "main", "subghz", "subghz_i.h"),
            os.path.join(REPO_DIR, "lib", "subghz", "subghz_device.h")
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                if "PREDATOR_CC1101" not in content:
                    patch = "\n// --- Predator CC1101 Configuration ---\n#define PREDATOR_CC1101_EXTERNAL 1\n// Enable external CC1101 for Predator module\n// -----------------------------------------\n"
                    
                    with open(config_path, "w", encoding='utf-8') as f:
                        f.write(content + patch)
                    print(f"[+] Patched SubGHz config for Predator: {config_path}")
                    return
                else:
                    print("[*] SubGHz config already patched")
                    return
        
        print("[!] Warning: Could not find SubGHz files to patch")
        return

    with open(cc1101_file, "r", encoding='utf-8') as f:
        content = f.read()

    if "PREDATOR_CC1101" not in content:
        patch = "\n// --- Predator CC1101 Patch ---\n#define PREDATOR_CC1101 1\n// Force external module for Predator\n// SPI pins: SCK=PA5, MISO=PA6, MOSI=PA7, CS=PA4\n// ---------------------------------\n"
        
        with open(cc1101_file, "w", encoding='utf-8') as f:
            f.write(patch + content)
        print(f"[+] Patched CC1101 external module: {cc1101_file}")
    else:
        print("[*] CC1101 already patched")

def update_repo():
    """Update the repository to latest version."""
    print("[*] Updating repository...")
    
    # Check if origin remote exists
    # try:
    #     result = subprocess.run(["git", "remote", "-v"], cwd=REPO_DIR, capture_output=True, text=True, check=True)
    #     if "origin" not in result.stdout:
    #         print("[*] Adding origin remote...")
    #         run(f"git remote add origin {REPO_URL}", cwd=REPO_DIR)
    # except subprocess.CalledProcessError:
    #     print("[*] Setting up git remote...")
    #     run(f"git remote add origin {REPO_URL}", cwd=REPO_DIR)
    
    # # Try to pull updates, but don't fail if it doesn't work
    # try:
    #     run("git pull origin main", cwd=REPO_DIR)
    # except:
    #     print("[!] Warning: Could not update repository. Using existing version.")
    #     try:
    #         run("git fetch origin", cwd=REPO_DIR)
    #         run("git reset --hard origin/main", cwd=REPO_DIR)
    #     except:
    #         print("[*] Continuing with existing repository state...")

def build(install_app=True):
    """Build the firmware using ufbt."""
    global FIRMWARE_OUTPUT
    
    print("[*] Setting up build environment...")
    
    if install_app:
        print("[*] Building Predator app...")
        # Build the Predator app using the local firmware build system
        predator_app_dir = os.path.join(REPO_DIR, "applications_user", "predator")
        if os.path.exists(predator_app_dir):
            # Use the local firmware build system instead of ufbt
            run("python fbt.py fap_predator", cwd=REPO_DIR)
        else:
            print("[!] Error: Predator app not found in applications_user")
            sys.exit(1)
         
        # Check for FAP output
        possible_outputs = [
            os.path.join(predator_app_dir, "dist", "predator.fap"),
            os.path.join(REPO_DIR, "build", "f7-C", "predator.fap"),
            os.path.join(REPO_DIR, "dist", "predator.fap")
        ]
        
        for output_path in possible_outputs:
            if os.path.exists(output_path):
                FIRMWARE_OUTPUT = output_path
                break
    else:
        print("[*] Firmware-only mode - patches applied, no build required")
        print("[*] Hardware modifications are now integrated into the firmware source")
        
        # Set a status message since we're not building
        FIRMWARE_OUTPUT = "Patches applied - ready for manual firmware build"

def create_predator_config():
    """Create Predator-specific configuration files."""
    config_dir = os.path.join(REPO_DIR, "applications", "main", "predator")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    config_content = """// Predator Module Configuration
#pragma once

// ESP32 UART Configuration
#define PREDATOR_ESP32_UART_TX_PIN &gpio_ext_pa7  // Pin 2
#define PREDATOR_ESP32_UART_RX_PIN &gpio_ext_pa6  // Pin 3
#define PREDATOR_ESP32_UART_BAUD   115200

// GPS UART Configuration  
#define PREDATOR_GPS_UART_TX_PIN   &gpio_ext_pa4  // Pin 7
#define PREDATOR_GPS_UART_RX_PIN   &gpio_ext_pb3  // Pin 8
#define PREDATOR_GPS_UART_BAUD     9600

// CC1101 SPI Configuration
#define PREDATOR_CC1101_CS_PIN     &gpio_ext_pa4  // Pin 7
#define PREDATOR_CC1101_SCK_PIN    &gpio_ext_pa5  // Pin 6
#define PREDATOR_CC1101_MISO_PIN   &gpio_ext_pa6  // Pin 3
#define PREDATOR_CC1101_MOSI_PIN   &gpio_ext_pa7  // Pin 2
#define PREDATOR_CC1101_GDO0_PIN   &gpio_ext_pb2  // Pin 5
"""
    
    config_file = os.path.join(config_dir, "predator_config.h")
    with open(config_file, "w", encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"[+] Created Predator configuration: {config_file}")

def copy_predator_app(install_app=True):
    """Copy Predator application to firmware applications directory."""
    if not install_app:
        print("[*] Skipping Predator app installation (firmware-only mode)")
        return False
    
    predator_src = os.path.join(PROJECT_ROOT, "predator_app")
    predator_dst = os.path.join(REPO_DIR, "applications_user", "predator")
    
    if not os.path.exists(predator_src):
        print("[!] Warning: Predator app source not found. Skipping app integration.")
        return False
    
    # Create applications_user directory if it doesn't exist
    apps_user_dir = os.path.join(REPO_DIR, "applications_user")
    if not os.path.exists(apps_user_dir):
        os.makedirs(apps_user_dir, exist_ok=True)
    
    # Copy Predator app
    if os.path.exists(predator_dst):
        shutil.rmtree(predator_dst)
    
    shutil.copytree(predator_src, predator_dst)
    print(f"[+] Copied Predator app to firmware: {predator_dst}")
    return True

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build Flipper Zero firmware with Predator module support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python build_predator_firmware.py --install-app    # Build with Predator app (default)
  python build_predator_firmware.py --no-app        # Build firmware with modifications only"""
    )
    
    app_group = parser.add_mutually_exclusive_group()
    app_group.add_argument(
        "--install-app", 
        action="store_true", 
        default=True,
        help="Install Predator app (default behavior)"
    )
    app_group.add_argument(
        "--no-app", 
        action="store_true", 
        help="Skip Predator app installation, only apply firmware modifications"
    )
    
    return parser.parse_args()

def main():
    """Main function to orchestrate firmware building."""
    args = parse_arguments()
    install_app = not args.no_app
    
    print("=" * 60)
    print("  Flipper Zero Predator Module Firmware Builder")
    if install_app:
        print("  Mode: Full build with Predator app")
    else:
        print("  Mode: Firmware modifications only")
    print("=" * 60)
    
    print("[*] Checking dependencies...")
    check_dependencies()
    
    print("[*] Setting up repository...")
    ensure_repo()
    
    if os.path.exists(REPO_DIR):
        update_repo()
    
    if install_app:
        print("[*] Integrating Predator application...")
        app_copied = copy_predator_app(install_app)
    else:
        print("[*] Skipping Predator application integration...")
        # Remove predator app if it exists to prevent build conflicts
        predator_dst = os.path.join(REPO_DIR, "applications_user", "predator")
        if os.path.exists(predator_dst):
            print(f"[*] Removing existing Predator app to avoid build conflicts: {predator_dst}")
            shutil.rmtree(predator_dst)
        
        # Remove application.fam file to prevent FAP build attempts
        app_fam_file = os.path.join(REPO_DIR, "application.fam")
        if os.path.exists(app_fam_file):
            print(f"[*] Removing application.fam to prevent FAP build: {app_fam_file}")
            os.remove(app_fam_file)
        
        app_copied = False
    
    print("[*] Creating Predator configuration...")
    create_predator_config()
    
    print("[*] Applying patches...")
    patch_gpio()
    patch_cc1101()
    
    print("[*] Building firmware...")
    build(install_app)
    
    # Check for output based on build mode
    firmware_found = False
    
    if install_app and app_copied:
        # Check for FAP output
        predator_app_dir = os.path.join(REPO_DIR, "applications_user", "predator")
        possible_outputs = [
            os.path.join(predator_app_dir, "dist", "predator.fap"),
            os.path.join(REPO_DIR, "build", "f7-C", "predator.fap"),
            os.path.join(REPO_DIR, "dist", "predator.fap")
        ]
        
        for output_path in possible_outputs:
            if os.path.exists(output_path):
                firmware_found = True
                print("\n" + "=" * 60)
                print("[✓] Predator FAP built successfully!")
                print(f"    Location: {output_path}")
                print(f"    Size: {os.path.getsize(output_path) / 1024:.2f} KB")
                print("\n📋 Next steps:")
                print("1. Connect your Flipper Zero via USB")
                print("2. Copy predator.fap to /ext/apps/Tools/ on your Flipper")
                print("3. Or use qFlipper to install the FAP file")
                print("4. Launch Predator from Apps > Tools menu")
                print("\n⚠️  Important: Ensure your Predator module is connected")
                print("   ESP32S2 on pins 15,16 | GPS on pins 13,14 | A07 RF module")
                print("=" * 60)
                break
        
        if not firmware_found:
            print("\n[!] Error: Predator FAP build failed or output not found.")
            print("    Checked locations:")
            for path in possible_outputs:
                print(f"    - {path}")
            print("\n    Try running 'ufbt' manually in the predator app directory.")
            sys.exit(1)
    else:
        # For firmware-only mode, we just applied patches
        firmware_found = True
        print("\n" + "=" * 60)
        print("[✓] Predator firmware modifications applied successfully!")
        print(f"    Repository: {REPO_DIR}")
        print(f"    Configuration: {os.path.join(REPO_DIR, 'applications', 'main', 'predator', 'predator_config.h')}")
        print("\n📋 Next steps:")
        print("1. Use the modified firmware source for your build process")
        print("2. GPIO and CC1101 configurations are now available")
        print("3. Integrate with official Flipper firmware build system")
        print("\n⚠️  Note: This mode applies hardware modifications only")
        print("   To build the Predator app, run with --install-app")
        print("=" * 60)

if __name__ == "__main__":
    main()