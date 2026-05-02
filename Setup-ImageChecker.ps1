# Setup-ImageChecker.ps1
# Run as Administrator — registers image-checker-daemon.ps1 as a scheduled task
# Daemon checks image paths every 30 seconds automatically

$HugoSite   = "C:\Users\DELL\karimabdelazizblog"
$Daemon     = "$HugoSite\image-checker-daemon.ps1"
$TaskName   = "KarimImageChecker"
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karim Blog - checks and fixes broken image paths every 30 seconds</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$currentUser</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-WindowStyle Hidden -ExecutionPolicy Bypass -File "$Daemon"</Arguments>
      <WorkingDirectory>$HugoSite</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$tmp = "$env:TEMP\KarimImageChecker.xml"
[System.IO.File]::WriteAllText($tmp, $taskXml, [System.Text.Encoding]::Unicode)

schtasks /Delete /TN $TaskName /F 2>&1 | Out-Null
schtasks /Create /TN $TaskName /XML $tmp /F
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK  Task '$TaskName' registered - runs every 30 seconds on logon." -ForegroundColor Green
    schtasks /Run /TN $TaskName
    Start-Sleep -Seconds 3
    $state = (schtasks /Query /TN $TaskName /FO LIST 2>&1 | Select-String 'Status:') -replace 'Status:\s*',''
    Write-Host "OK  Daemon status: $state" -ForegroundColor Green
    Write-Host "    Log: $HugoSite\image-checker.log" -ForegroundColor Yellow
} else {
    Write-Host "FAIL  Could not register task. Run as Administrator." -ForegroundColor Red
}
