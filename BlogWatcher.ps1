# ============================================================
#  BlogWatcher.ps1  —  Karim's Blog Auto-Deploy Watcher
#  Runs silently in the background on every Windows startup.
#
#  What it does every time you save a post in Obsidian:
#    1. Syncs your Obsidian posts  →  Hugo content/posts
#    2. Copies images into per-post subfolders in static/images/
#    3. Builds the Hugo static site
#    4. Commits + pushes to GitHub
#    5. Cloudflare Pages auto-deploys to karimabdelazizblog.tech
# ============================================================

# =====================================================================
# ██████╗  EDIT ONLY THIS BLOCK  ██████╗
# =====================================================================

# Full path to your Obsidian "posts" folder
# (images are found automatically in sibling folders like "active recon images")
$ObsidianPostsPath  = "C:\Users\DELL\Documents\Obsidian Vault\posts"

# Full path to your Hugo site root
$HugoSitePath       = "C:\Users\DELL\karimabdelazizblog"

# Git branch to push to (Cloudflare Pages watches this)
$GitBranch          = "main"

# How many seconds to wait after a file change before deploying
# (gives Obsidian time to finish writing the file)
$DebounceSeconds    = 8

# Minimum gap between two deploys (prevents rapid-fire triggers)
$CooldownSeconds    = 30

# =====================================================================
# DO NOT EDIT BELOW THIS LINE
# =====================================================================

$HugoPostsPath    = "$HugoSitePath\content\posts"
$StaticImagesPath = "$HugoSitePath\static\images"
$ImagesScript     = "$HugoSitePath\images.py"
$LogFile          = "$HugoSitePath\watcher.log"

$global:LastDeploy  = [DateTime]::MinValue
$global:IsDeploying = $false

# ─── Detect Python ────────────────────────────────────────────────────
$PythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $PythonCmd = $cmd
        break
    }
}

# ─── Logging ──────────────────────────────────────────────────────────
function Write-Log {
    param(
        [string]$Msg,
        [ValidateSet("INFO","WARN","ERROR","STEP","OK")][string]$Level = "INFO"
    )
    $icons = @{ INFO="·"; WARN="⚠"; ERROR="✖"; STEP="→"; OK="✔" }
    $ts    = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line  = "[$ts][$Level] $($icons[$Level]) $Msg"

    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

# ─── Main Deploy Function ─────────────────────────────────────────────
function Invoke-BlogDeploy {
    # Debounce guard
    if ($global:IsDeploying) {
        Write-Log "Deploy already running — skipped." "WARN"
        return
    }
    $elapsed = ([DateTime]::Now - $global:LastDeploy).TotalSeconds
    if ($elapsed -lt $CooldownSeconds) {
        Write-Log "Cooldown ($([int]$elapsed)s < ${CooldownSeconds}s) — skipped." "WARN"
        return
    }

    $global:IsDeploying = $true
    $global:LastDeploy  = [DateTime]::Now

    try {
        Write-Log "══════════════ DEPLOY START ══════════════" "INFO"

        # ── Step 1: Sync Obsidian posts ──────────────────────────────
        Write-Log "Syncing posts from Obsidian..." "STEP"
        # /XD excludes image folders (they go to static/images/, not content/posts/)
        $null = robocopy `
            $ObsidianPostsPath `
            $HugoPostsPath `
            /MIR /Z /W:2 /R:2 /NFL /NDL /NJH /NJS `
            /XF "*.png" "*.jpg" "*.jpeg" "*.gif" "*.webp" "*.svg" "*.bmp"
        if ($LASTEXITCODE -ge 8) {
            throw "Robocopy failed with exit code $LASTEXITCODE"
        }
        Write-Log "Posts synced." "OK"

        # ── Step 2: Process images into per-post subfolders ──────────
        Write-Log "Processing images (per-post subfolders)..." "STEP"
        if ($null -eq $PythonCmd) {
            throw "Python not found. Install Python and add it to PATH."
        }
        # images.py now searches sibling image folders automatically
        # (e.g. "active recon images/" next to "Active Reconnaissance.md")
        & $PythonCmd $ImagesScript $ObsidianPostsPath $StaticImagesPath
        if ($LASTEXITCODE -ne 0) {
            throw "images.py exited with code $LASTEXITCODE"
        }
        Write-Log "Images processed." "OK"

        # ── Step 3: Hugo build ───────────────────────────────────────
        Write-Log "Building Hugo site..." "STEP"
        Push-Location $HugoSitePath
        $hugoOut = hugo 2>&1
        $hugoOut | ForEach-Object { Write-Log "  $_" }
        if ($LASTEXITCODE -ne 0) {
            throw "Hugo build failed. Check config/theme."
        }
        Write-Log "Hugo build complete." "OK"

        # ── Step 4: Git commit + push ────────────────────────────────
        Write-Log "Committing and pushing to GitHub..." "STEP"
        git add . 2>&1 | Out-Null

        $dirty = git status --porcelain 2>&1
        if ($dirty) {
            $commitMsg = "Auto-deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            git commit -m $commitMsg 2>&1 | Out-Null
            git push origin $GitBranch 2>&1 | ForEach-Object { Write-Log "  git: $_" }
            if ($LASTEXITCODE -ne 0) {
                throw "git push failed. Check SSH keys / credentials."
            }
            Write-Log "Pushed to GitHub. Cloudflare will deploy in ~30s." "OK"
        } else {
            Write-Log "No changes to commit — already up to date." "OK"
        }

        Write-Log "══════════════ DEPLOY DONE  ══════════════" "INFO"

    } catch {
        Write-Log "DEPLOY FAILED: $_" "ERROR"
    } finally {
        $global:IsDeploying = $false
        Pop-Location -ErrorAction SilentlyContinue
    }
}

# ─── Pre-flight Checks ────────────────────────────────────────────────
$null = New-Item -ItemType Directory -Path $LogFile -Force -ErrorAction SilentlyContinue
Remove-Item $LogFile -Force -ErrorAction SilentlyContinue

Write-Log "Starting Karim's Blog Watcher..."

$missingPaths = @(
    $ObsidianPostsPath,
    $ObsidianAttachPath,
    $HugoSitePath,
    $ImagesScript
) | Where-Object { -not (Test-Path $_) }

if ($missingPaths) {
    $missingPaths | ForEach-Object { Write-Log "Missing path: $_" "ERROR" }
    Write-Log "Fix the paths in the EDIT THIS BLOCK section, then re-run." "ERROR"
    exit 1
}

# Ensure output directories exist
$null = New-Item -Path $StaticImagesPath -ItemType Directory -Force
$null = New-Item -Path $HugoPostsPath    -ItemType Directory -Force

Write-Log "Python  : $PythonCmd"
Write-Log "Hugo    : $(hugo version 2>&1 | Select-Object -First 1)"
Write-Log "Git     : $(git --version 2>&1)"
Write-Log "Watching: $ObsidianPostsPath"
Write-Log "Log     : $LogFile"
Write-Log "Press Ctrl+C in this window to stop (normally runs hidden)."

# ─── FileSystemWatcher ────────────────────────────────────────────────
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path                  = $ObsidianPostsPath
$watcher.Filter                = "*.md"
$watcher.NotifyFilter          = (
    [IO.NotifyFilters]::LastWrite -bor
    [IO.NotifyFilters]::FileName  -bor
    [IO.NotifyFilters]::DirectoryName
)
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents   = $true

Write-Log "Watcher armed. Waiting for Obsidian saves..." "OK"

# ─── Main Loop ────────────────────────────────────────────────────────
# WaitForChanged blocks until a file change occurs or the timeout expires.
# This is more CPU-friendly than polling in a tight loop.
while ($true) {
    try {
        $change = $watcher.WaitForChanged([IO.WatcherChangeTypes]::All, 60000)

        if (-not $change.TimedOut) {
            Write-Log "Change detected: $($change.Name)"
            Write-Log "Waiting ${DebounceSeconds}s for file to finish saving..."
            Start-Sleep -Seconds $DebounceSeconds
            Invoke-BlogDeploy
        }
        # If timed out: just loop again (heartbeat — keeps the process alive)

    } catch {
        Write-Log "Watcher loop error: $_ — restarting in 10s." "ERROR"
        Start-Sleep -Seconds 10
    }
}
