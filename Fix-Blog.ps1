# ============================================================
#  Fix-Blog.ps1  Run this ONCE to clean up all image issues
#
#  What it does:
#    1. Stops the watcher
#    2. Cleans up duplicate/broken image folders in static/
#    3. Renames Obsidian image folders to use hyphens not spaces
#    4. Fixes image links inside all .md files in Hugo content/
#    5. Removes garbage files
#    6. Rebuilds Hugo and pushes to GitHub
#    7. Restarts the watcher
# ============================================================

$HugoSitePath      = "C:\Users\DELL\karimabdelazizblog"
$ObsidianPostsPath = "C:\Users\DELL\Documents\Obsidian Vault\posts"
$StaticImagesPath  = "$HugoSitePath\static\images"
$HugoPostsPath     = "$HugoSitePath\content\posts"
$TaskName          = "KarimBlogWatcher"

function OK   { Write-Host "  OK  $args" -ForegroundColor Green }
function STEP { Write-Host "`n>>> $args" -ForegroundColor Cyan }
function WARN { Write-Host "  WARN  $args" -ForegroundColor Yellow }
function INFO { Write-Host "  $args" -ForegroundColor White }

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "  Fix-Blog.ps1 - Full Cleanup and Repair"     -ForegroundColor Cyan
Write-Host "=============================================`n" -ForegroundColor Cyan

# ── Step 1: Stop the watcher ──────────────────────────────
STEP "Step 1: Stopping the watcher..."
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
OK "Watcher stopped."

# ── Step 2: Clean garbage files from Hugo site ────────────
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

# ── Step 3: Fix static/images folder names ────────────────
STEP "Step 3: Fixing image folder names in static/images/..."

if (Test-Path $StaticImagesPath) {
    $folders = Get-ChildItem -Path $StaticImagesPath -Directory
    foreach ($folder in $folders) {
        $oldName = $folder.Name
        $newName = $oldName -replace '\s+', '-'
        if ($oldName -ne $newName) {
            $oldPath = $folder.FullName
            $newPath = Join-Path $StaticImagesPath $newName
            if (Test-Path $newPath) {
                INFO "Merging '$oldName' into existing '$newName'..."
                Get-ChildItem -Path $oldPath | ForEach-Object {
                    $dest = Join-Path $newPath $_.Name
                    if (-not (Test-Path $dest)) {
                        Move-Item $_.FullName $newPath -Force
                    }
                }
                Remove-Item $oldPath -Recurse -Force
                OK "Merged and removed: $oldName"
            } else {
                Rename-Item $oldPath $newName
                OK "Renamed: $oldName to $newName"
            }
        } else {
            INFO "Already clean: $oldName"
        }
    }
} else {
    WARN "Static images folder not found: $StaticImagesPath"
}

# ── Step 4: Fix image links inside Hugo content .md files ──
STEP "Step 4: Fixing image links in Hugo content/posts/ .md files..."

$mdFiles = Get-ChildItem -Path $HugoPostsPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$fixedFiles = 0

foreach ($mdFile in $mdFiles) {
    $content = Get-Content $mdFile.FullName -Raw -Encoding UTF8
    $original = $content

    # Fix image paths: replace spaces in folder names with hyphens
    $content = [regex]::Replace($content,
        '!\[([^\]]*)\]\(/images/([^/\)]+)/([^\)]+)\)',
        {
            param($m)
            $alt    = $m.Groups[1].Value
            $folder = $m.Groups[2].Value -replace '\s+', '-'
            $file   = $m.Groups[3].Value
            "![$alt](/images/$folder/$file)"
        }
    )

    # Remove any leftover Obsidian wiki-link image embeds
    $content = $content -replace '!\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]', ''
    $content = $content -replace '\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]', ''

    if ($content -ne $original) {
        $content | Set-Content $mdFile.FullName -Encoding UTF8 -NoNewline
        OK "Fixed links in: $($mdFile.Name)"
        $fixedFiles++
    } else {
        INFO "No changes needed: $($mdFile.Name)"
    }
}
OK "Fixed $fixedFiles file(s)."

# ── Step 5: Fix Obsidian image folder names ───────────────
STEP "Step 5: Fixing image folder names in Obsidian vault..."

$obsidianFolders = Get-ChildItem -Path $ObsidianPostsPath -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'images' -and $_.Name -match '\s' }

foreach ($folder in $obsidianFolders) {
    $oldName = $folder.Name
    $newName = $oldName -replace '\s+', '-'
    $newPath = Join-Path $folder.Parent.FullName $newName

    if (-not (Test-Path $newPath)) {
        Rename-Item $folder.FullName $newName
        OK "Renamed Obsidian folder: $oldName to $newName"
    } else {
        INFO "Already correct: $newName"
    }
}

# ── Step 6: Run images.py to reprocess everything ─────────
STEP "Step 6: Re-running images.py..."
$pythonResult = & python "$HugoSitePath\images.py" $ObsidianPostsPath $StaticImagesPath 2>&1
$pythonResult | ForEach-Object { INFO $_ }
if ($LASTEXITCODE -eq 0) {
    OK "images.py completed successfully."
} else {
    WARN "images.py had warnings. Check output above."
}

# ── Step 7: Hugo build ────────────────────────────────────
STEP "Step 7: Building Hugo site..."
Push-Location $HugoSitePath
$hugoOut = hugo 2>&1
$hugoOut | ForEach-Object { INFO $_ }
if ($LASTEXITCODE -eq 0) {
    OK "Hugo build complete."
} else {
    WARN "Hugo build had issues. Check output above."
}

# ── Step 8: Git commit and push ───────────────────────────
STEP "Step 8: Committing and pushing to GitHub..."
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

# ── Step 9: Restart watcher ───────────────────────────────
STEP "Step 9: Restarting the watcher..."
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2
$state = (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue).State
OK "Watcher status: $state"

# ── Done ──────────────────────────────────────────────────
Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "  ALL DONE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Cloudflare will redeploy in ~30 seconds." -ForegroundColor White
Write-Host "  Check your blog at:" -ForegroundColor White
Write-Host "  https://karimabdelazizblog.pages.dev" -ForegroundColor Yellow
Write-Host "  https://karimabdelazizblog.tech" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Going forward name your image folders like this:" -ForegroundColor White
Write-Host "  NoteName-images   use hyphens not spaces" -ForegroundColor Yellow
Write-Host "  Example: Introduction-to-information-gathering-images" -ForegroundColor Yellow
Write-Host ""