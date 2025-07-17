#!/usr/bin/env python3
"""
Fix Chrome Files

This script copies essential Chrome files from the versioned directory
to the Application directory so Chrome can launch properly.
"""

import shutil
from pathlib import Path

def fix_chrome_files():
    """Copy essential Chrome files to the Application directory."""
    
    print("🔧 Fixing Chrome file structure...")
    
    chrome_app_dir = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application")
    version_dir = chrome_app_dir / "138.0.7204.101"
    
    if not version_dir.exists():
        print(f"❌ Version directory not found: {version_dir}")
        return False
    
    # Essential files that Chrome needs in the Application directory
    essential_files = [
        "icudtl.dat",
        "chrome_elf.dll",
        "resources.pak",
        "chrome_100_percent.pak",
        "chrome_200_percent.pak",
        "v8_context_snapshot.bin",
        "libEGL.dll",
        "libGLESv2.dll"
    ]
    
    copied_files = []
    failed_files = []
    
    for file_name in essential_files:
        src_file = version_dir / file_name
        dst_file = chrome_app_dir / file_name
        
        try:
            if src_file.exists():
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                    copied_files.append(file_name)
                    print(f"✅ Copied: {file_name}")
                else:
                    print(f"⚠️ Already exists: {file_name}")
            else:
                failed_files.append(file_name)
                print(f"❌ Source not found: {file_name}")
        except Exception as e:
            failed_files.append(file_name)
            print(f"❌ Failed to copy {file_name}: {e}")
    
    # Copy Locales directory if it doesn't exist
    src_locales = version_dir / "Locales"
    dst_locales = chrome_app_dir / "Locales"
    
    try:
        if src_locales.exists() and not dst_locales.exists():
            shutil.copytree(src_locales, dst_locales)
            print(f"✅ Copied Locales directory")
        elif dst_locales.exists():
            print(f"⚠️ Locales directory already exists")
        else:
            print(f"❌ Source Locales directory not found")
    except Exception as e:
        print(f"❌ Failed to copy Locales directory: {e}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Files copied: {len(copied_files)}")
    print(f"❌ Files failed: {len(failed_files)}")
    
    if failed_files:
        print(f"Failed files: {', '.join(failed_files)}")
    
    return len(failed_files) == 0

def verify_chrome_files():
    """Verify that essential Chrome files are in place."""
    
    print("\n🔍 Verifying Chrome files...")
    
    chrome_app_dir = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application")
    
    essential_files = [
        "chrome.exe",
        "icudtl.dat",
        "chrome_elf.dll",
        "resources.pak"
    ]
    
    all_present = True
    
    for file_name in essential_files:
        file_path = chrome_app_dir / file_name
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file_name} ({file_size:,} bytes)")
        else:
            print(f"❌ {file_name} - MISSING")
            all_present = False
    
    # Check Locales directory
    locales_dir = chrome_app_dir / "Locales"
    if locales_dir.exists():
        locale_count = len(list(locales_dir.glob("*.pak")))
        print(f"✅ Locales directory ({locale_count} locale files)")
    else:
        print(f"❌ Locales directory - MISSING")
        all_present = False
    
    return all_present

def main():
    """Main function."""
    
    print("🔧 Chrome File Structure Fix")
    print("=" * 40)
    
    # Fix Chrome files
    fix_success = fix_chrome_files()
    
    # Verify Chrome files
    verify_success = verify_chrome_files()
    
    print(f"\n{'='*40}")
    if fix_success and verify_success:
        print("🎉 Chrome file structure fixed successfully!")
        print("Chrome should now be able to launch properly.")
        return 0
    else:
        print("❌ Chrome file structure fix incomplete.")
        print("Some files may still be missing.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
