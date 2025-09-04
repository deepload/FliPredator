#!/usr/bin/env python3
import os
import subprocess
import sys

def test_build():
    """Test build the predator app using ufbt"""
    predator_app_dir = os.path.join(os.path.dirname(__file__), "predator_app")
    
    if not os.path.exists(predator_app_dir):
        print("Error: predator_app directory not found")
        return False
    
    print(f"Testing build in: {predator_app_dir}")
    
    try:
        # Change to predator app directory
        os.chdir(predator_app_dir)
        
        # Try to build with ufbt
        result = subprocess.run(
            ["ufbt", "build"], 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Build timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"Error during build: {e}")
        return False

if __name__ == "__main__":
    success = test_build()
    sys.exit(0 if success else 1)
