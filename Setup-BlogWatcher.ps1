# ============================================================
#  Setup-BlogWatcher.ps1  —  Run this ONCE as Administrator
#
#  What it does:
#    1. Validates that all required tools are installed
#    2. Creates Git repo + pushes initial commit
#    3. Registers BlogWatcher.ps1 in Windows Task Scheduler
#       so it auto-starts silently on every login/restart
#    4. Starts the watcher immediately
# ============================================================

# ── EDIT THESE (must match BlogWatcher.ps1) ───────────────
$HugoSitePath = "C:\Users\DELL\karimabdelazizblog"
$GitRemoteURL = "git@github.com:Karim-A-37/karimabdelazizblog.git"
$GitBranch    = "main"
# ──────────────────────────────────────────────────────────

$WatcherScript = "$HugoSitePath\BlogWatcher.ps1"
$TaskName      = "KarimBlogWatcher"

# ─── Helper ───────────────────────────────────────────────
function Step { param([int]$n, [string]$msg) Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function OK   { Write-Host "    OK $args" -ForegroundColor Green }
function Warn { Write-Host "    WARN $args" -ForegroundColor Yellow }
function Fail { Write-Host "    FAIL $args" -ForegroundColor Red; exit 1 }

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "  Karim's Blog Watcher - One-Time Setup"       -ForegroundColor Cyan
Write-Host "=============================================`n" -ForegroundColor Cyan

# ── Step 1: Check Admin ───────────────────────────────────
Step 1 "Checking Administrator privileges..."
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Fail "Please right-click this script and choose Run as Administrator."
}
OK "Running as Administrator."

# ── Step 2: Check required tools ─────────────────────────
Step 2 "Checking required tools..."

$tools = @{
    "git"    = "https://git-scm.com/download/win"
    "hugo"   = "https://gohugo.io/installation/"
    "python" = "https://python.org/downloads/"
}

foreach ($tool in $tools.Keys) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        $ver = & $tool --version 2>&1 | Select-Object -First 1
        OK "$tool : $ver"
    } else {
        if ($tool -eq "python" -and (Get-Command "python3" -ErrorAction SilentlyContinue)) {
            OK "python3 found"
        } else {
            Fail "$tool is not installed. Download: $($tools[$tool])"
        }
    }
}

# ── Step 3: Validate paths ────────────────────────────────
Step 3 "Checking paths..."

if (-not (Test-Path $HugoSitePath)) {
    Fail "Hugo site not found at: $HugoSitePath"
}
OK "Hugo site found: $HugoSitePath"

if (-not (Test-Path $WatcherScript)) {
    Fail "BlogWatcher.ps1 not found at: $WatcherScript"
}
OK "BlogWatcher.ps1 found."

if (-not (Test-Path "$HugoSitePath\images.py")) {
    Fail "images.py not found at: $HugoSitePath\images.py"
}
OK "images.py found."

# ── Step 4: Set PowerShell execution policy ───────────────
Step 4 "Setting PowerShell execution policy..."
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
OK "Execution policy set to RemoteSigned."

# ── Step 5: Initialize Git repo ───────────────────────────
Step 5 "Setting up Git repository..."

Push-Location $HugoSitePath

if (-not (Test-Path ".git")) {
    git init
    git remote add origin $GitRemoteURL
    OK "Git repo initialized."
} else {
    $remotes = git remote 2>&1
    if ($remotes -notcontains "origin") {
        git remote add origin $GitRemoteURL
        OK "Remote origin added."
    } else {
        OK "Git repo already initialized."
    }
}

# Create .gitignore if missing
if (-not (Test-Path ".gitignore")) {
    $gitignoreContent = "resources/" + [Environment]::NewLine + ".hugo_build.lock" + [Environment]::NewLine + "watcher.log"
    Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding UTF8
    OK ".gitignore created."
}

# Initial commit + push
hugo 2>&1 | Out-Null
git add .
$dirty = git status --porcelain
if ($dirty) {
    git commit -m "Initial blog setup"
    git push -u origin $GitBranch
    OK "Initial push to GitHub complete."
} else {
    OK "Nothing to commit - repo already up to date."
}

Pop-Location

# ── Step 6: Register Task Scheduler ───────────────────────
Step 6 "Registering auto-start task in Windows Task Scheduler..."

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Warn "Old task removed."
}

$psExe  = "powershell.exe"
$psArgs = "-WindowStyle Hidden -ExecutionPolicy Bypass -NonInteractive -File `"$WatcherScript`""

$action   = New-ScheduledTaskAction -Execute $psExe -Argument $psArgs
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable $true

$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName  $TaskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -Principal $principal `
    -Force | Out-Null

OK "Task '$TaskName' registered in Task Scheduler."

# ── Step 7: Start watcher now ─────────────────────────────
Step 7 "Starting the watcher right now..."
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2

$taskInfo = Get-ScheduledTask -TaskName $TaskName
OK "Watcher status: $($taskInfo.State)"

# ── Done ──────────────────────────────────────────────────
Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  What happens now:" -ForegroundColor White
Write-Host "  - The watcher runs silently in the background" -ForegroundColor White
Write-Host "  - Every time you save a .md file in Obsidian, it auto-deploys" -ForegroundColor White
Write-Host "  - It restarts automatically after every reboot/login" -ForegroundColor White
Write-Host ""
Write-Host "  Log file:" -ForegroundColor White
Write-Host "  $HugoSitePath\watcher.log" -ForegroundColor Yellow
Write-Host ""
Write-Host "  To stop the watcher:" -ForegroundColor White
Write-Host "  Stop-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  To check status:" -ForegroundColor White
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  To remove completely:" -ForegroundColor White
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Yellow
Write-Host ""