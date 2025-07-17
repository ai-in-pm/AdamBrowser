# Chrome Management Suite PowerShell Launcher
Write-Host "Chrome Management Suite - Adam Browser" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$env:CHROME_MGMT_ROOT = "D:\science_projects\adam_browser"
$env:PYTHONPATH = "$env:CHROME_MGMT_ROOT;$env:PYTHONPATH"

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Green
Write-Host "  1. Build distribution packages"
Write-Host "  2. Update Chrome"
Write-Host "  3. Optimize installation"
Write-Host "  4. Run tests"
Write-Host "  5. Start auto-updater"
Write-Host "  6. Show status"
Write-Host "  7. Run complete cycle"
Write-Host ""

$choice = Read-Host "Enter your choice (1-7)"

switch ($choice) {
    "1" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" build }
    "2" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" update }
    "3" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" optimize }
    "4" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" test }
    "5" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" auto-update }
    "6" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" status }
    "7" { & python "D:\science_projects\adam_browser/chrome_management_suite.py" all }
    default { Write-Host "Invalid choice" -ForegroundColor Red }
}

Read-Host "Press Enter to exit"
