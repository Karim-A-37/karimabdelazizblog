# Find and kill all image-checker related processes
$procs = Get-WmiObject Win32_Process
foreach ($p in $procs) {
    $cmd = $p.CommandLine
    if ($cmd -and ($cmd -like '*image-checker*' -or $cmd -like '*image_checker*')) {
        Write-Host "FOUND PID $($p.ProcessId): $cmd"
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "KILLED PID $($p.ProcessId)"
    }
}

# Also show all powershell command lines so we can identify the daemon
Write-Host "`n--- All powershell.exe processes ---"
foreach ($p in $procs) {
    if ($p.Name -eq 'powershell.exe') {
        Write-Host "PID $($p.ProcessId) | Started: $($p.CreationDate) | CMD: $($p.CommandLine)"
    }
}
