Stop-ScheduledTask -TaskName 'KarimBlogWatcher' -ErrorAction SilentlyContinue

$files = @(
    'C:\Users\DELL\Documents\Obsidian Vault\posts\ejpt\Day-0\Introduction to information gathering.md',
    'C:\Users\DELL\karimabdelazizblog\content\posts\ejpt\Day-0\Introduction to information gathering.md'
)

$newFront = @"
---
title: "Introduction to information gathering"
date: 2026-05-01
slug: "introduction-to-information-gathering"
draft: false
tags:
  - ejpt
  - recon
---

"@

foreach ($f in $files) {
    if (-not (Test-Path $f)) { Write-Host "Not found: $f"; continue }
    $body = Get-Content $f -Raw -Encoding UTF8
    # Strip existing frontmatter (--- ... ---) from the top
    $body = [regex]::Replace($body, '(?s)^---.*?---\s*\n+', '')
    $final = $newFront + $body.TrimStart()
    [System.IO.File]::WriteAllText($f, $final, [System.Text.Encoding]::UTF8)
    Write-Host "Patched: $f"
}

# Also fix image links in the Hugo content file to use correct slug path
$hugoMd = 'C:\Users\DELL\karimabdelazizblog\content\posts\ejpt\Day-0\Introduction to information gathering.md'
if (Test-Path $hugoMd) {
    $c = Get-Content $hugoMd -Raw -Encoding UTF8
    # Fix relative image links: ![alt](scope.png) or ![alt](images/scope.png)
    $c = [regex]::Replace($c,
        '!\[([^\]]*)\]\((?!http|/)([^)]+\.(png|jpg|jpeg|gif|webp|svg|bmp))\)',
        {
            param($m)
            $alt  = $m.Groups[1].Value
            $file = [System.IO.Path]::GetFileName($m.Groups[2].Value)
            $name = [System.IO.Path]::GetFileNameWithoutExtension($file) -replace '\s+','-'
            $ext  = [System.IO.Path]::GetExtension($file).ToLower()
            return "![$alt](/images/ejpt/day-0/introduction-to-information-gathering/$name$ext)"
        }
    )
    [System.IO.File]::WriteAllText($hugoMd, $c, [System.Text.Encoding]::UTF8)
    Write-Host "Fixed image links in Hugo content md."
}

# Build Hugo and push
Set-Location 'C:\Users\DELL\karimabdelazizblog'
hugo 2>&1 | ForEach-Object { Write-Host $_ }

git add . 2>&1 | Out-Null
$dirty = git status --porcelain 2>&1
if ($dirty) {
    git commit -m "Fix: slug + image links in frontmatter" 2>&1 | Out-Null
    git push origin main 2>&1 | ForEach-Object { Write-Host "git: $_" }
    Write-Host "Pushed. Cloudflare deploys in ~30s."
} else {
    Write-Host "Nothing to commit."
}

Start-ScheduledTask -TaskName 'KarimBlogWatcher' -ErrorAction SilentlyContinue
Write-Host "Watcher restarted."
