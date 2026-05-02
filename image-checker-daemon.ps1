# image-checker-daemon.ps1
# Runs image-checker.py every 30 seconds in background
# Registered as a scheduled task via Setup-ImageChecker.ps1

$HugoSite  = "C:\Users\DELL\karimabdelazizblog"
$Script    = "$HugoSite\image-checker.py"
$LogFile   = "$HugoSite\image-checker.log"

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Write-Log "INFO  image-checker-daemon started. Checking every 30 seconds."

while ($true) {
    try {
        $result = & python $Script 2>&1
        # Only log lines that aren't "All image links OK"
        foreach ($line in $result) {
            if ($line -notmatch "image links OK|run started|run done") {
                Write-Log "  $line"
            }
        }
    } catch {
        Write-Log "ERROR $_"
    }
    Start-Sleep -Seconds 30
}
