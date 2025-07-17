#!/usr/bin/env python3
"""
File Organization Script

This script organizes the Adam Browser project files into appropriate folders.
"""

import os
import shutil
from pathlib import Path

def organize_files():
    """Organize files into appropriate folders."""
    
    project_root = Path(r"D:\science_projects\adam_browser")
    
    # Define folder structure
    folders = {
        'tests': [
            'test_enhanced_training_button.py',
            'test_chrome_integration.py',
            'test_url_detection_simple.py',
            'test_expedia_training.py',
            'test_general_training.py',
            'test_complete_training_system.py',
            'test_chrome_functionality.py',
            'test_chrome_launch.py',
            'test_advanced_agent.py'
        ],
        'chrome_management': [
            'chrome_management_suite.py',
            'chrome_management_launcher.ps1',
            'chrome_management_launcher.bat',
            'chrome_management_demo.log'
        ],
        'training': [
            'train_expedia_agent.py',
            'general_webpage_trainer.py',
            'travel_booking_patterns.py',
            'expedia_training_module.py',
            'expedia_training_data.json',
            'expedia_element_detector.py',
            'adam_browser_advanced_capabilities.py'
        ],
        'demos': [
            'demo_floating_agent_chrome.py',
            'demo_chrome_management.py'
        ],
        'docs': [
            'EXPEDIA_TRAINING_README.md',
            'ADVANCED_FEATURES_README.md'
        ],
        'scripts': [
            'fix_chrome_files.py'
        ]
    }
    
    print("🗂️ Organizing Adam Browser project files...")
    print("=" * 50)
    
    # Create directories
    for folder_name in folders.keys():
        folder_path = project_root / folder_name
        folder_path.mkdir(exist_ok=True)
        print(f"📁 Created/verified directory: {folder_name}")
    
    # Move files
    moved_files = 0
    failed_files = []
    
    for folder_name, file_list in folders.items():
        print(f"\n📂 Moving files to {folder_name}/")
        
        for file_name in file_list:
            src_file = project_root / file_name
            dst_file = project_root / folder_name / file_name
            
            try:
                if src_file.exists():
                    if dst_file.exists():
                        print(f"  ⚠️ {file_name} already exists in {folder_name}, skipping")
                    else:
                        shutil.move(str(src_file), str(dst_file))
                        print(f"  ✅ Moved: {file_name}")
                        moved_files += 1
                else:
                    print(f"  ❌ Not found: {file_name}")
                    failed_files.append(file_name)
            except Exception as e:
                print(f"  ❌ Failed to move {file_name}: {e}")
                failed_files.append(file_name)
    
    print(f"\n{'='*50}")
    print("📊 ORGANIZATION SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Files moved: {moved_files}")
    print(f"❌ Files failed: {len(failed_files)}")
    
    if failed_files:
        print(f"\nFailed files:")
        for file_name in failed_files:
            print(f"  - {file_name}")
    
    # Show final directory structure
    print(f"\n📁 FINAL DIRECTORY STRUCTURE:")
    print(f"{'='*30}")
    
    for folder_name in folders.keys():
        folder_path = project_root / folder_name
        if folder_path.exists():
            files_in_folder = list(folder_path.glob("*.py")) + list(folder_path.glob("*.md")) + list(folder_path.glob("*.json")) + list(folder_path.glob("*.bat")) + list(folder_path.glob("*.ps1")) + list(folder_path.glob("*.log"))
            print(f"\n📂 {folder_name}/ ({len(files_in_folder)} files)")
            for file_path in sorted(files_in_folder):
                print(f"  📄 {file_path.name}")
    
    return moved_files, failed_files

def main():
    """Main function."""
    try:
        moved, failed = organize_files()
        
        if len(failed) == 0:
            print(f"\n🎉 File organization completed successfully!")
            print(f"All {moved} files have been moved to their appropriate folders.")
            return 0
        else:
            print(f"\n⚠️ File organization completed with some issues.")
            print(f"{moved} files moved successfully, {len(failed)} files failed.")
            return 1
            
    except Exception as e:
        print(f"❌ File organization failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
