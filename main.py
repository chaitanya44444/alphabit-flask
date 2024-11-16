import os
import subprocess
import sys

def install_packages():
    packages = ["flask==2.1.0", "werkzeug==2.1.0"]
    for package in packages:
        try:
            __import__(package.split("==")[0])  
        except ImportError:
            print(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
    
    os.environ["PORT"] = os.environ.get("PORT", "5000")
    
    try:
        subprocess.check_call([sys.executable, "app.py"])
    except FileNotFoundError:
        print("app.py not found. Make sure it is in the same directory as this script.")
