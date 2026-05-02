# Setup-ImageChecker.ps1
# Run as Administrator — registers image-checker.py as a scheduled task every 15 min

$HugoSite   = "C:\Users\DELL\karimabdelazizblog"
$Script     = "$HugoSite\image-checker.py"
$TaskName   = "KarimImageChecker"
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karim Blog - checks and fixes broken image paths every 15 min</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT15M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2026-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
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
    <ExecutionTimeLimit>PT5M</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"$Script"</Arguments>
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
    Write-Host "OK  Task '$TaskName' registered - runs every 15 minutes." -ForegroundColor Green
    schtasks /Run /TN $TaskName
    Write-Host "OK  First run triggered. Log: $HugoSite\image-checker.log" -ForegroundColor Green
} else {
    Write-Host "FAIL  Could not register task. Run as Administrator." -ForegroundColor Red
}
