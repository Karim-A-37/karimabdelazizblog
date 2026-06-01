param()
$ErrorActionPreference = "Continue"
$Site    = "C:\Users\DELL\karimabdelazizblog"
$Content = "$Site\content"
$UTF8NB  = New-Object System.Text.UTF8Encoding($false)
$raw     = "https://raw.githubusercontent.com/Karim-A-37/Wazuh/main"

function Step($n,$t){ Write-Host "`n[$n] $t" -ForegroundColor Cyan }
function OK($t)     { Write-Host "  OK  $t"  -ForegroundColor Green }
function ERR($t)    { Write-Host "  ERR $t"  -ForegroundColor Red }

# ── 1. Ensure dirs exist ──────────────────────────────────────────────────
Step 1 "Ensuring directories exist"
New-Item "$Content\projects\wazuh" -ItemType Directory -Force | Out-Null
OK "projects/wazuh/"

# ── 2. Download labs ──────────────────────────────────────────────────────
Step 2 "Downloading Wazuh labs from GitHub"

$labs = @(
    @{
        Url  = "$raw/Lab%201/lab-1.md"
        Dest = "$Content\projects\wazuh\lab-1.md"
        FM   = "title: `"Lab 1 - Wazuh + Suricata IDS Setup`"`ndate: 2025-10-31`nslug: wazuh-lab-1-ids-setup`ndescription: `"Setting up Wazuh SIEM with Suricata NIDS to detect port scans, SQL injection, XSS, and Tor connections using Emerging Threats rules.`"`ntags:`n  - wazuh`n  - suricata`n  - ids`n  - siem`nseries: [`"Wazuh Labs`"]`nweight: 1`ndraft: false`nShowToc: true`nTocOpen: false"
    },
    @{
        Url  = "$raw/Lab%202/Lab-2.md"
        Dest = "$Content\projects\wazuh\lab-2.md"
        FM   = "title: `"Lab 2 - Malware Detection with Wazuh`"`ndate: 2025-12-09`nslug: wazuh-lab-2-malware-detection`ndescription: `"Malware detection using Wazuh FIM, CDB hash lists, VirusTotal integration, Windows Defender log forwarding, and Sysmon for fileless malware detection.`"`ntags:`n  - wazuh`n  - malware`n  - fim`n  - virustotal`n  - sysmon`nseries: [`"Wazuh Labs`"]`nweight: 2`ndraft: false`nShowToc: true`nTocOpen: false"
    },
    @{
        Url  = "$raw/Lab%203/N8N_Blockchain_AI.md"
        Dest = "$Content\projects\wazuh\lab-3.md"
        FM   = "title: `"Lab 3 - SetChain: AI + Blockchain Threat Detection`"`ndate: 2026-05-25`nslug: wazuh-lab-3-setchain`ndescription: `"Graduation project: fully automated cybersecurity pipeline combining Wazuh, Suricata, n8n, a 5-layer AI model (Isolation Forest + XGBoost + LLM), STIX 2.1, IPFS, and Hyperledger Fabric blockchain.`"`ntags:`n  - wazuh`n  - ai`n  - blockchain`n  - hyperledger`n  - n8n`n  - ipfs`n  - graduation-project`nseries: [`"Wazuh Labs`"]`nweight: 3`ndraft: false`nShowToc: true`nTocOpen: false"
    }
)

foreach ($lab in $labs) {
    try {
        $body = (Invoke-WebRequest -Uri $lab.Url -UseBasicParsing -TimeoutSec 30).Content
        # Strip any accidental leading frontmatter
        if ($body -match "(?s)^---.*?---\s*`n") {
            $body = ($body -split "(?s)^---.*?---\s*`n", 2)[1]
        }
        $full = "---`n$($lab.FM)`n---`n`n$($body.TrimStart())"
        [System.IO.File]::WriteAllText($lab.Dest, $full, $UTF8NB)
        OK (Split-Path $lab.Dest -Leaf)
    } catch {
        ERR "Download failed: $($lab.Url) — $_"
    }
}

# ── 3. Patch eJPT posts (add series) ─────────────────────────────────────
Step 3 "Adding series frontmatter to eJPT posts"

$ejpt = @(
    "$Content\posts\ejpt\Day-0\Introduction to information gathering.md",
    "$Content\posts\ejpt\Day-1\Passive Reconnaissance.md"
)
foreach ($p in $ejpt) {
    if (-not (Test-Path $p)) { ERR "Not found: $p"; continue }
    $txt = [System.IO.File]::ReadAllText($p, $UTF8NB)
    if ($txt -match 'series:') { OK "Already patched: $(Split-Path $p -Leaf)"; continue }
    $txt = $txt -replace '(draft:\s*false)', "draft: false`nseries: [`"eJPT`"]`nShowToc: true`nTocOpen: false"
    [System.IO.File]::WriteAllText($p, $txt, $UTF8NB)
    OK "Patched: $(Split-Path $p -Leaf)"
}

# ── 4. Hugo build ─────────────────────────────────────────────────────────
Step 4 "Hugo build"
Push-Location $Site
$out = hugo 2>&1
$out | ForEach-Object { Write-Host "  $_" }
$code = $LASTEXITCODE
Pop-Location
if ($code -eq 0) { OK "Build successful" } else { ERR "Build failed (exit $code)" }

# ── 5. Git commit + push ──────────────────────────────────────────────────
Step 5 "Git commit and push"
Push-Location $Site
git add . | Out-Null
git commit -m "Blog upgrade: Wazuh labs, sections, search, eJPT series, Projects nav"
git push origin main 2>&1 | ForEach-Object { Write-Host "  $_" }
Pop-Location

Write-Host "`nDone!" -ForegroundColor Green
