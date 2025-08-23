#!/usr/bin/env python3
"""
Revolutionary Scraper System Setup
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Revolutionary Scraper Setup")
    print("=" * 50)
    
    # Kontrollera Python-version
    if sys.version_info < (3, 8, 0):
        print("❌ Python 3.8+ krävs")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Installera requirements
    print("📦 Installerar requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", 
            "requirements_revolutionary.txt"
        ])
        print("✅ Requirements installerade")
    except subprocess.CalledProcessError:
        print("❌ Fel vid installation av requirements")
        return False
    except FileNotFoundError:
        print("❌ requirements_revolutionary.txt hittades inte")
        return False
    
    # Installera Playwright
    print("🎭 Installerar Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Playwright installerat")
    except subprocess.CalledProcessError:
        print("⚠️ Playwright installation misslyckades - fortsätter ändå")
    
    # Skapa konfigurationsfil
    config_content = '''# Revolutionary Scraper Configuration
CONFIG = {
    "proxy_rotator": {
        "bright_data": {
            "enabled": False,
            "username": "your_username_here",
            "password": "your_password_here"
        }
    },
    "captcha_solver": {
        "2captcha": {
            "enabled": False,
            "api_key": "your_api_key_here"
        }
    }
}
'''
    
    try:
        with open("config_template.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Config template skapad")
    except Exception as e:
        print(f"❌ Kunde inte skapa config: {e}")
    
    print("\n🎉 SETUP KLAR!")
    print("📝 Nästa steg:")
    print("1. Kopiera config_template.py till config.py")
    print("2. Fyll i dina API-nycklar")
    print("3. Testa systemet med main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
