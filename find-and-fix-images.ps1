# find-and-fix-images.ps1
# Finds the two missing Pasted images and copies them to static/images

$VaultRoot   = "C:\Users\DELL\Documents\Obsidian Vault"
$StaticDest  = "C:\Users\DELL\karimabdelazizblog\static\images\ejpt\day-1\passive-reconnaissance"

# The missing files as slugified names
$missing = @(
    "pasted-image-20260429121012",
    "pasted-image-20260429123335"
)

# Search vault for any image matching the date pattern
$found = Get-ChildItem -Path $VaultRoot -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(png|jpg|jpeg|gif|webp)' -and $_.Name -match '20260429' }

Write-Host "Found $($found.Count) matching file(s) in vault:"
$found | ForEach-Object { Write-Host "  $($_.FullName)" }

# Copy each one with the slugified name
New-Item -Path $StaticDest -ItemType Directory -Force | Out-Null

foreach ($file in $found) {
    # Slugify: lowercase, spaces to hyphens, remove special chars
    $slug = $file.BaseName.ToLower() -replace '\s+', '-' -replace '[^a-z0-9\-]', ''
    $ext  = $file.Extension.ToLower()
    $dest = Join-Path $StaticDest "$slug$ext"
    Copy-Item $file.FullName $dest -Force
    Write-Host "COPIED: $($file.Name) -> $slug$ext"
}

Write-Host "Done."
