# PowerShell script to create Windows shortcut for Adam Browser v1
# Run this script to create a .lnk shortcut file

Write-Host "Creating shortcut for Adam Browser - Embedded Chrome Agent v1..." -ForegroundColor Green

# Define paths
$ScriptPath = "D:\science_projects\adam_browser\embedded_chrome_floating_agent_v1.py"
$ShortcutPath = "D:\science_projects\adam_browser\examples\Adam Browser - Embedded Chrome Agent v1.lnk"
$PythonExe = "C:\Program Files\Python311\python.exe"

# Check if Python exists
if (-not (Test-Path $PythonExe)) {
    # Try to find Python in PATH
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) {
        Write-Host "Error: Python not found. Please install Python or update the path in this script." -ForegroundColor Red
        exit 1
    }
}

# Create the shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "`"$ScriptPath`""
$Shortcut.WorkingDirectory = "D:\science_projects\adam_browser"
$Shortcut.Description = "Adam Browser - Embedded Chrome Agent v1 - AI-powered browser automation"
$Shortcut.Save()

Write-Host "✅ Shortcut created successfully!" -ForegroundColor Green
Write-Host "📁 Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host "🎯 Target: $ScriptPath" -ForegroundColor Cyan
Write-Host "🐍 Python: $PythonExe" -ForegroundColor Cyan

Write-Host "`n🚀 How to use:" -ForegroundColor Yellow
Write-Host "• Double-click the .lnk file to run the application" -ForegroundColor White
Write-Host "• Or use the .bat file for a console version" -ForegroundColor White
Write-Host "• The floating robot icon will appear in the bottom-right corner" -ForegroundColor White
Write-Host "• Single-click the robot to open the Chrome chat interface" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
