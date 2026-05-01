# ============================================================
#  Fix-Blog.ps1 — Run this ONCE to clean up all image issues
#
#  What it does:
#    1.  Stops the watcher task
#    2.  Removes garbage files from Hugo site
#    3.  Fixes static/images/ folder names (spaces → hyphens)
#    4.  Fixes image links inside Hugo content/ .md files
#    5.  Fixes Obsidian vault image folder names (spaces → hyphens)
#    6.  Re-runs images.py to reprocess everything
#    7.  Syncs Obsidian posts → Hugo content/posts via robocopy
#    8.  Rebuilds Hugo site
#    9.  Commits and pushes to GitHub
#    10. Restarts the watcher task
# ============================================================

$HugoSitePath      = "C:\Users\DELL\karimabdelazizblog"
$ObsidianPostsPath = "C:\Users\DELL\Documents\Obsidian Vault\posts"
$StaticImagesPath  = "$HugoSitePath\static\images"
$HugoPostsPath     = "$HugoSitePath\content\posts"
$TaskName          = "KarimBlogWatcher"
$ImagesScript      = "$HugoSitePath\images.py"

# ─── Output helpers ───────────────────────────────────────────────────────────
function OK   { param([string]$msg) Write-Host "  OK   $msg" -ForegroundColor Green  }
function STEP { param([string]$msg) Write-Host "`n>>> $msg" -ForegroundColor Cyan    }
function WARN { param([string]$msg) Write-Host "  WARN $msg" -ForegroundColor Yellow }
function INFO { param([string]$msg) Write-Host "  $msg"     -ForegroundColor White  }
function ERR  { param([string]$msg) Write-Host "  ERR  $msg" -ForegroundColor Red   }

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "  Fix-Blog.ps1 - Full Cleanup and Repair"     -ForegroundColor Cyan
Write-Host "=============================================`n" -ForegroundColor Cyan

# ── Step 1: Stop the watcher ──────────────────────────────────────────────────
STEP "Step 1: Stopping the watcher..."
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
OK "Watcher stopped."

# ── Step 2: Remove garbage files from Hugo site ───────────────────────────────
STEP "Step 2: Removing garbage files from Hugo site..."
$garbage = @("*.tmp", "Thumbs.db", ".DS_Store", "desktop.ini", "*.log.bak")
foreach ($pattern in $garbage) {
    $found = Get-ChildItem -Path $HugoSitePath -Filter $pattern -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($f in $found) {
        Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
        INFO "Deleted: $($f.FullName)"
    }
}
OK "Garbage cleanup done."

# ── Step 3: Fix static/images/ folder names (spaces → hyphens, merge dupes) ──
STEP "Step 3: Fixing image folder names in static/images/..."

function Rename-FoldersRecursive {
    param([string]$BasePath)
    if (-not (Test-Path $BasePath)) { return }

    # Process deepest folders first to avoid path-not-found after rename
    $folders = Get-ChildItem -Path $BasePath -Directory -Recurse -ErrorAction SilentlyContinue |
               Sort-Object { $_.FullName.Length } -Descending

    foreach ($folder in $folders) {
        $oldName = $folder.Name
        $newName = $oldName -replace '\s+', '-'
        if ($oldName -eq $newName) {
            INFO "Already clean: $oldName"
            continue
        }

        $oldPath = $folder.FullName
        # Re-check folder still exists (parent may have been renamed already)
        if (-not (Test-Path $oldPath)) { continue }

        $newPath = Join-Path $folder.Parent.FullName $newName

        if (Test-Path $newPath) {
            INFO "Merging '$oldName' into existing '$newName'..."
            Get-ChildItem -Path $oldPath | ForEach-Object {
                $dest = Join-Path $newPath $_.Name
                if (-not (Test-Path $dest)) {
                    Move-Item $_.FullName $newPath -Force -ErrorAction SilentlyContinue
                }
            }
            Remove-Item $oldPath -Recurse -Force -ErrorAction SilentlyContinue
            OK "Merged and removed: $oldName"
        } else {
            Rename-Item -Path $oldPath -NewName $newName -Force -ErrorAction SilentlyContinue
            OK "Renamed: $oldName -> $newName"
        }
    }
}

Rename-FoldersRecursive -BasePath $StaticImagesPath

# Also rename image filenames that have spaces
if (Test-Path $StaticImagesPath) {
    $imageFiles = Get-ChildItem -Path $StaticImagesPath -Recurse -File -ErrorAction SilentlyContinue
    foreach ($img in $imageFiles) {
        $oldName = $img.Name
        $newName = $oldName -replace '\s+', '-'
        if ($oldName -ne $newName) {
            $newPath = Join-Path $img.DirectoryName $newName
            if (-not (Test-Path $newPath)) {
                Rename-Item $img.FullName $newName -Force -ErrorAction SilentlyContinue
                OK "Renamed file: $oldName -> $newName"
            }
        }
    }
}

OK "Static images cleanup done."

# ── Step 4: Fix image links inside Hugo content/ .md files ───────────────────
STEP "Step 4: Fixing image links in Hugo content/posts/ .md files..."

$mdFiles   = Get-ChildItem -Path $HugoPostsPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$fixedFiles = 0

foreach ($mdFile in $mdFiles) {
    $content  = Get-Content $mdFile.FullName -Raw -Encoding UTF8
    $original = $content

    # Fix: replace spaces in /images/... folder/file names with hyphens
    $content = [regex]::Replace(
        $content,
        '!\[([^\]]*)\]\((/images/[^)]+)\)',
        {
            param($m)
            $alt = $m.Groups[1].Value
            $url = $m.Groups[2].Value

            # Slugify each segment of the path (preserve extension on last segment)
            $segments = $url -split '/'
            $fixed = $segments | ForEach-Object {
                $seg = $_
                if ($seg -eq '' -or $seg -eq 'images') { return $seg }
                # If it has an extension, handle name and extension separately
                if ($seg -match '^(.+)(\.[^.]+)$') {
                    $name = $Matches[1] -replace '\s+', '-'
                    $ext  = $Matches[2].ToLower()
                    return "$name$ext"
                }
                return ($seg -replace '\s+', '-')
            }
            $fixedUrl = $fixed -join '/'
            return "![$alt]($fixedUrl)"
        }
    )

    # Remove leftover Obsidian wiki-link image embeds that were never converted
    $content = $content -replace '!\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\]\]', ''
    $content = $content -replace '\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\]\]', ''

    if ($content -ne $original) {
        $content | Set-Content $mdFile.FullName -Encoding UTF8 -NoNewline
        OK "Fixed links in: $($mdFile.Name)"
        $fixedFiles++
    } else {
        INFO "No changes needed: $($mdFile.Name)"
    }
}
OK "Fixed $fixedFiles file(s)."

# ── Step 5: Fix Obsidian vault image folder names (spaces → hyphens) ─────────
STEP "Step 5: Fixing image folder names in Obsidian vault..."

$obsidianFolders = Get-ChildItem -Path $ObsidianPostsPath -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '\s' } |
    Sort-Object { $_.FullName.Length } -Descending

foreach ($folder in $obsidianFolders) {
    $oldName = $folder.Name
    $newName = $oldName -replace '\s+', '-'
    if ($oldName -eq $newName) { continue }

    $oldPath = $folder.FullName
    if (-not (Test-Path $oldPath)) { continue }

    $newPath = Join-Path $folder.Parent.FullName $newName
    if (-not (Test-Path $newPath)) {
        Rename-Item $oldPath $newName -Force -ErrorAction SilentlyContinue
        OK "Renamed Obsidian folder: $oldName -> $newName"
    } else {
        INFO "Already exists: $newName"
    }
}
OK "Obsidian folders fixed."

# ── Step 6: Sync Obsidian posts → Hugo content/posts ─────────────────────────
STEP "Step 6: Syncing Obsidian posts to Hugo content/posts..."
$null = New-Item -Path $HugoPostsPath -ItemType Directory -Force

$roboOut = robocopy `
    $ObsidianPostsPath `
    $HugoPostsPath `
    /MIR /Z /W:2 /R:2 /NFL /NDL /NJH /NJS /E `
    /XF "*.png" "*.jpg" "*.jpeg" "*.gif" "*.webp" "*.svg" "*.bmp" 2>&1

if ($LASTEXITCODE -ge 8) {
    WARN "Robocopy reported issues (exit $LASTEXITCODE). Check above output."
} else {
    OK "Posts synced."
}

# ── Step 7: Run images.py to reprocess everything ────────────────────────────
STEP "Step 7: Re-running images.py..."

# Detect Python
$PythonCmd = $null
foreach ($cmd in @("python", "py", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $PythonCmd = $cmd
        break
    }
}

if ($null -eq $PythonCmd) {
    ERR "Python not found in PATH. Install Python 3 and add it to PATH."
} elseif (-not (Test-Path $ImagesScript)) {
    ERR "images.py not found at: $ImagesScript"
} else {
    $pythonResult = & $PythonCmd $ImagesScript $ObsidianPostsPath $StaticImagesPath 2>&1
    $pythonResult | ForEach-Object { INFO $_ }
    if ($LASTEXITCODE -eq 0) {
        OK "images.py completed successfully."
    } else {
        WARN "images.py had warnings — check output above."
    }
}

# ── Step 8: Hugo build ────────────────────────────────────────────────────────
STEP "Step 8: Building Hugo site..."
Push-Location $HugoSitePath
$hugoOut = hugo 2>&1
$hugoOut | ForEach-Object { INFO $_ }
if ($LASTEXITCODE -eq 0) {
    OK "Hugo build complete."
} else {
    WARN "Hugo build had issues. Check output above."
}

# ── Step 9: Git commit and push ───────────────────────────────────────────────
STEP "Step 9: Committing and pushing to GitHub..."
git add . 2>&1 | Out-Null
$dirty = git status --porcelain 2>&1
if ($dirty) {
    $msg = "Fix: cleanup image folders and links $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git commit -m $msg 2>&1 | Out-Null
    git push origin main 2>&1 | ForEach-Object { INFO "git: $_" }
    if ($LASTEXITCODE -eq 0) {
        OK "Pushed to GitHub. Cloudflare will deploy in ~30s."
    } else {
        WARN "Git push failed. Try manually: git push origin main"
    }
} else {
    OK "Nothing new to commit."
}
Pop-Location

# ── Step 10: Restart watcher ──────────────────────────────────────────────────
STEP "Step 10: Restarting the watcher..."
Start-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$state = (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue).State
if ($state) {
    OK "Watcher status: $state"
} else {
    WARN "Could not find task '$TaskName'. Run Setup-BlogWatcher.ps1 to register it."
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "  ALL DONE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Cloudflare will redeploy in ~30 seconds." -ForegroundColor White
Write-Host "  Check your blog at:" -ForegroundColor White
Write-Host "  https://karimabdelazizblog.pages.dev" -ForegroundColor Yellow
Write-Host "  https://karimabdelazizblog.tech" -ForegroundColor Yellow
Write-Host ""
Write-Host "  HOW TO STRUCTURE YOUR OBSIDIAN POSTS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  posts/" -ForegroundColor White
Write-Host "    ejpt/" -ForegroundColor White
Write-Host "      Day-0/" -ForegroundColor White
Write-Host "        My-Note.md" -ForegroundColor White
Write-Host "        My-Note-images/" -ForegroundColor White
Write-Host "          scope.png" -ForegroundColor White
Write-Host "          diagram.png" -ForegroundColor White
Write-Host ""
Write-Host "  Rule: use hyphens in folder names (no spaces)." -ForegroundColor Yellow
Write-Host "  Images auto-publish at /images/ejpt/day-0/my-note/" -ForegroundColor Yellow
Write-Host ""