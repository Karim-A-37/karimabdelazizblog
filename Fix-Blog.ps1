# ============================================================
#  Fix-Blog.ps1 — Run this ONCE to clean up all image issues
#
#  What it does (in order):
#    1.  Stops the watcher task
#    2.  Removes garbage files from Hugo site
#    3.  Fixes static/images/ folder + file names  (spaces → hyphens)
#    4.  Fixes image links inside Hugo content/posts .md files
#    5.  Fixes Obsidian vault image folder names  (spaces → hyphens)
#    6.  Syncs Obsidian posts → Hugo content/posts via robocopy
#    7.  Runs images.py  (Job 1: Obsidian vault  |  Job 2: rescue content/)
#    8.  Removes image folders that were rescued from content/ to static/
#    9.  Rebuilds Hugo site
#    10. Commits and pushes to GitHub
#    11. Restarts the watcher task
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
function INFO { param([string]$msg) Write-Host "  $msg"      -ForegroundColor White  }
function ERR  { param([string]$msg) Write-Host "  ERR  $msg" -ForegroundColor Red    }

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

# ── Step 3: Fix static/images/ folder + file names ───────────────────────────
STEP "Step 3: Fixing names in static/images/ (spaces -> hyphens)..."

if (Test-Path $StaticImagesPath) {
    # Rename folders deepest-first to avoid broken paths after parent rename
    $folders = Get-ChildItem -Path $StaticImagesPath -Directory -Recurse -ErrorAction SilentlyContinue |
               Sort-Object { $_.FullName.Length } -Descending

    foreach ($folder in $folders) {
        $oldName = $folder.Name
        $newName = $oldName -replace '\s+', '-'
        if ($oldName -eq $newName) { continue }
        $oldPath = $folder.FullName
        if (-not (Test-Path $oldPath)) { continue }
        $newPath = Join-Path $folder.Parent.FullName $newName
        if (Test-Path $newPath) {
            # Merge into existing
            Get-ChildItem -Path $oldPath | ForEach-Object {
                $dest = Join-Path $newPath $_.Name
                if (-not (Test-Path $dest)) {
                    Move-Item $_.FullName $newPath -Force -ErrorAction SilentlyContinue
                }
            }
            Remove-Item $oldPath -Recurse -Force -ErrorAction SilentlyContinue
            OK "Merged: $oldName -> $newName"
        } else {
            Rename-Item -Path $oldPath -NewName $newName -Force -ErrorAction SilentlyContinue
            OK "Renamed folder: $oldName -> $newName"
        }
    }

    # Rename image files with spaces
    Get-ChildItem -Path $StaticImagesPath -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '\s' } |
        ForEach-Object {
            $newName = $_.Name -replace '\s+', '-'
            $newPath = Join-Path $_.DirectoryName $newName
            if (-not (Test-Path $newPath)) {
                Rename-Item $_.FullName $newName -Force -ErrorAction SilentlyContinue
                OK "Renamed file: $($_.Name) -> $newName"
            }
        }
}
OK "static/images/ cleanup done."

# ── Step 4: Fix image links inside Hugo content/ .md files ───────────────────
STEP "Step 4: Fixing image links in Hugo content/posts/ .md files..."

$mdFiles    = Get-ChildItem -Path $HugoPostsPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$fixedFiles = 0

foreach ($mdFile in $mdFiles) {
    $content  = Get-Content $mdFile.FullName -Raw -Encoding UTF8
    $original = $content

    # Fix spaces inside /images/... URLs (folder names and filenames)
    $content = [regex]::Replace(
        $content,
        '!\[([^\]]*)\]\((/images/[^)]+)\)',
        {
            param($m)
            $alt      = $m.Groups[1].Value
            $urlParts = $m.Groups[2].Value -split '/'
            $fixed    = $urlParts | ForEach-Object {
                $seg = $_
                if ($seg -eq '' -or $seg -eq 'images') { return $seg }
                if ($seg -match '^(.+)(\.[^.]+)$') {
                    return ($Matches[1] -replace '\s+', '-') + $Matches[2].ToLower()
                }
                return ($seg -replace '\s+', '-')
            }
            return "![$alt]($($fixed -join '/'))"
        }
    )

    # Remove leftover Obsidian wiki-link embeds
    $content = $content -replace '!\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\]\]', ''
    $content = $content -replace  '\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\]\]', ''

    if ($content -ne $original) {
        $content | Set-Content $mdFile.FullName -Encoding UTF8 -NoNewline
        OK "Fixed links in: $($mdFile.Name)"
        $fixedFiles++
    } else {
        INFO "No changes: $($mdFile.Name)"
    }
}
OK "Fixed $fixedFiles file(s)."

# ── Step 4b: Ensure frontmatter + fix relative image links in Hugo content ───
STEP "Step 4b: Injecting missing frontmatter and fixing relative image links..."

$mdFiles2   = Get-ChildItem -Path $HugoPostsPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$fmFixed    = 0

foreach ($mdFile in $mdFiles2) {
    $content  = Get-Content $mdFile.FullName -Raw -Encoding UTF8
    $original = $content

    # Derive slug and title from filename
    $postName = [System.IO.Path]::GetFileNameWithoutExtension($mdFile.Name)
    $slug     = ($postName -replace '\s+', '-').ToLower() -replace '[^a-z0-9\-]', '' -replace '-{2,}', '-'
    $title    = $postName
    $today    = Get-Date -Format "yyyy-MM-dd"

    # Determine image URL prefix from relative subfolder path inside content/posts
    $relDir   = [System.IO.Path]::GetDirectoryName(
                    (Resolve-Path $mdFile.FullName).Path.Substring(
                        (Resolve-Path $HugoPostsPath).Path.Length + 1))
    $slugParts = ($relDir -split '\\|/' | Where-Object { $_ -ne '' } |
                  ForEach-Object { ($_ -replace '\s+','-').ToLower() -replace '[^a-z0-9\-]','' })
    $imgPrefix = (($slugParts + $slug) -join '/')

    # Fix relative image links: ![alt](scope.png) or ![alt](images/scope.png)
    $content = [regex]::Replace(
        $content,
        '!\[([^\]]*)\]\((?!http|/)([^)]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\)',
        {
            param($m)
            $alt  = $m.Groups[1].Value
            $file = [System.IO.Path]::GetFileName($m.Groups[2].Value)
            $nm   = ([System.IO.Path]::GetFileNameWithoutExtension($file) -replace '\s+', '-').ToLower()
            $ext  = [System.IO.Path]::GetExtension($file).ToLower()
            return "![$alt](/images/$using:imgPrefix/$nm$ext)"
        }
    )

    # Inject missing frontmatter fields (slug, date, draft)
    $fmMatch = [regex]::Match($content, '(?s)^---\s*\n(.*?)\n---\s*\n')
    if ($fmMatch.Success) {
        $fmBody  = $fmMatch.Groups[1].Value.Trim()
        $changed = $false

        if ($fmBody -eq '') {
            # Empty frontmatter — rewrite completely
            $newFm   = "---`ntitle: `"$title`"`ndate: $today`nslug: `"$slug`"`ndraft: false`n---`n`n"
            $content = $newFm + $content.Substring($fmMatch.Index + $fmMatch.Length).TrimStart()
            $changed = $true
        } else {
            if ($fmBody -notmatch 'slug\s*:') {
                $fmBody += "`nslug: `"$slug`""
                $changed = $true
            }
            if ($fmBody -notmatch 'date\s*:') {
                $fmBody += "`ndate: $today"
                $changed = $true
            }
            if ($fmBody -notmatch 'draft\s*:') {
                $fmBody += "`ndraft: false"
                $changed = $true
            }
            if ($changed) {
                $newFm   = "---`n$($fmBody.Trim())`n---`n`n"
                $content = $newFm + $content.Substring($fmMatch.Index + $fmMatch.Length).TrimStart()
            }
        }
    } else {
        # No frontmatter at all — prepend it
        $newFm   = "---`ntitle: `"$title`"`ndate: $today`nslug: `"$slug`"`ndraft: false`n---`n`n"
        $content = $newFm + $content.TrimStart()
    }

    if ($content -ne $original) {
        [System.IO.File]::WriteAllText($mdFile.FullName, $content, [System.Text.Encoding]::UTF8)
        OK "Frontmatter/links fixed: $($mdFile.Name)"
        $fmFixed++
    } else {
        INFO "No frontmatter changes: $($mdFile.Name)"
    }
}
OK "Frontmatter fixed in $fmFixed file(s)."


# ── Step 5: Fix Obsidian vault image folder names ─────────────────────────────
STEP "Step 5: Fixing image folder names in Obsidian vault (spaces -> hyphens)..."

if (Test-Path $ObsidianPostsPath) {
    Get-ChildItem -Path $ObsidianPostsPath -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '\s' } |
        Sort-Object { $_.FullName.Length } -Descending |
        ForEach-Object {
            $newName = $_.Name -replace '\s+', '-'
            $newPath = Join-Path $_.Parent.FullName $newName
            if (-not (Test-Path $newPath)) {
                Rename-Item $_.FullName $newName -Force -ErrorAction SilentlyContinue
                OK "Renamed: $($_.Name) -> $newName"
            }
        }
    OK "Obsidian vault folders fixed."
} else {
    WARN "Obsidian posts path not found: $ObsidianPostsPath"
    INFO "Only Hugo content rescue will run."
}

# ── Step 6: Sync Obsidian posts → Hugo content/posts ─────────────────────────
STEP "Step 6: Syncing Obsidian posts to Hugo content/posts..."
New-Item -Path $HugoPostsPath -ItemType Directory -Force | Out-Null
if (Test-Path $ObsidianPostsPath) {
    robocopy $ObsidianPostsPath $HugoPostsPath /MIR /Z /W:2 /R:2 /NFL /NDL /NJH /NJS /E /XF "*.png" "*.jpg" "*.jpeg" "*.gif" "*.webp" "*.svg" "*.bmp" | Out-Null
    if ($LASTEXITCODE -ge 8) {
        WARN "Robocopy issues (exit $LASTEXITCODE). Some files may not have synced."
    } else {
        OK "Posts synced."
    }
} else {
    WARN "Obsidian posts path missing - skipping sync. Hugo content/posts used as-is."
}

# ── Step 7: Run images.py (Job1: Obsidian  |  Job2: rescue content/) ─────────
STEP "Step 7: Running images.py..."

$PythonCmd = $null
foreach ($cmd in @("python", "py", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { $PythonCmd = $cmd; break }
}

if ($null -eq $PythonCmd) {
    ERR "Python not found in PATH. Install Python 3 from python.org and add to PATH."
} elseif (-not (Test-Path $ImagesScript)) {
    ERR "images.py not found at: $ImagesScript"
} else {
    & $PythonCmd $ImagesScript $ObsidianPostsPath $StaticImagesPath $HugoPostsPath | ForEach-Object { INFO $_ }
    if ($LASTEXITCODE -eq 0) {
        OK "images.py completed successfully."
    } else {
        WARN "images.py had warnings - check output above."
    }
}

# -- Step 7b: Validate and fix broken image paths ---------------------------
STEP "Step 7b: Running image-checker.py..."
$ImageCheckerScript = "$HugoSitePath\image-checker.py"
if (Test-Path $ImageCheckerScript) {
    & $PythonCmd $ImageCheckerScript | ForEach-Object { INFO $_ }
    OK "Image paths checked."
} else {
    WARN "image-checker.py not found - skipping."
}

# -- Step 7c: Fix broken/duplicate frontmatter ------------------------------
STEP "Step 7c: Running fix-frontmatter.py..."
$FrontmatterScript = "$HugoSitePath\fix-frontmatter.py"
if (Test-Path $FrontmatterScript) {
    & $PythonCmd $FrontmatterScript | ForEach-Object { INFO $_ }
    OK "Frontmatter checked."
} else {
    WARN "fix-frontmatter.py not found - skipping."
}

# -- Step 8: Remove image folders rescued from content/ --------------------
STEP "Step 8: Cleaning up image folders from Hugo content/posts/..."
$imageFolders = Get-ChildItem -Path $HugoPostsPath -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'images' }

$removed = 0
foreach ($folder in $imageFolders) {
    # Only remove if all its files are already in static/images
    $imgFiles = Get-ChildItem -Path $folder.FullName -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -match '\.(png|jpg|jpeg|gif|webp|svg|bmp)$' }

    $allCopied = $true
    foreach ($img in $imgFiles) {
        # Check if a file with matching slug name exists anywhere in static/images
        $slugName = ($img.BaseName -replace '\s+', '-').ToLower() + $img.Extension.ToLower()
        $found    = Get-ChildItem -Path $StaticImagesPath -Filter $slugName -Recurse -ErrorAction SilentlyContinue
        if (-not $found) { $allCopied = $false; break }
    }

    if ($allCopied -and $imgFiles.Count -gt 0) {
        Remove-Item $folder.FullName -Recurse -Force -ErrorAction SilentlyContinue
        OK "Removed from content/: $($folder.Name)"
        $removed++
    } else {
        INFO "Keeping (not yet in static/): $($folder.Name)"
    }
}
OK "Removed $removed image folder(s) from content/."

# ── Step 9: Hugo build ────────────────────────────────────────────────────────
STEP "Step 9: Building Hugo site..."
Push-Location $HugoSitePath
$hugoOut = hugo 2>&1
$hugoOut | ForEach-Object { INFO $_ }
if ($LASTEXITCODE -eq 0) {
    OK "Hugo build complete."
} else {
    WARN "Hugo build had issues. Check output above."
}

# ── Step 10: Git commit and push ──────────────────────────────────────────────
STEP "Step 10: Committing and pushing to GitHub..."
git add . 2>&1 | Out-Null
$dirty = git status --porcelain 2>&1
if ($dirty) {
    $msg = "Fix: images + cleanup $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git commit -m $msg 2>&1 | Out-Null
    git push origin main 2>&1 | ForEach-Object { INFO "git: $_" }
    if ($LASTEXITCODE -eq 0) {
        OK "Pushed to GitHub. Cloudflare deploys in ~30s."
    } else {
        WARN "Git push failed. Try: git push origin main"
    }
} else {
    OK "Nothing new to commit."
}
Pop-Location

# ── Step 11: Restart watcher ──────────────────────────────────────────────────
STEP "Step 11: Restarting the watcher..."
Start-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$state = (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue).State
if ($state) { OK "Watcher status: $state" }
else        { WARN "Task not found. Run Setup-BlogWatcher.ps1 to register it." }

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "  ALL DONE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Blog: https://karimabdelazizblog.pages.dev" -ForegroundColor Yellow
Write-Host "  Blog: https://karimabdelazizblog.tech"      -ForegroundColor Yellow
Write-Host ""
Write-Host "  CORRECT OBSIDIAN STRUCTURE:" -ForegroundColor Cyan
Write-Host "  posts/"                       -ForegroundColor White
Write-Host "    ejpt/"                      -ForegroundColor White
Write-Host "    Day-0/"                     -ForegroundColor White
Write-Host "      My-Note.md"              -ForegroundColor White
Write-Host "      My-Note-images/"         -ForegroundColor White
Write-Host "        scope.png"             -ForegroundColor White
Write-Host ""
Write-Host "  Rule: use hyphens in ALL folder names, no spaces." -ForegroundColor Yellow
Write-Host ""