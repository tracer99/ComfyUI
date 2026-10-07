[CmdletBinding()]
param(
    [ValidateSet("DirectML", "QNN")]
    [string]$Runtime = "DirectML",
    [switch]$CpuOnly,
    [switch]$SafeMode,
    [ValidateRange(1, 65535)]
    [int]$Port = 8188,
    [string[]]$WhitelistCustomNodes = @()
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$serverPort = $Port
$serverUrl = "http://127.0.0.1:$serverPort"
$existingListener = Get-NetTCPConnection -LocalPort $serverPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existingListener) {
    try {
        $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($existingListener.OwningProcess)" -ErrorAction Stop
        $venvName = if ($Runtime -eq "QNN") { ".venv-qnn" } else { ".venv" }
        $projectPython = Join-Path $root "$venvName\Scripts\python.exe"
        if ($owner.CommandLine -match '(?i)\bmain\.py\b' -and $owner.ExecutablePath -eq $projectPython) {
            Write-Host "ComfyUI is already running at $serverUrl. Reusing the existing instance."
            try {
                Start-Process $serverUrl | Out-Null
            } catch {
            }
            return
        }
    } catch {
    }
}

& "$PSScriptRoot\bootstrap-arm.ps1" -Quiet -Runtime $Runtime
. "$PSScriptRoot\arm-common.ps1"

$runtimeName = Get-ArmRuntimeName -Runtime $Runtime
$env:COMFYUI_ARM_RUNTIME = $runtimeName.ToLowerInvariant()

if ($runtimeName -eq "QNN") {
    $CpuOnly = $true
}

$python = Resolve-ArmPythonInvoker -Runtime $runtimeName
if (-not $python) {
    throw "No Python interpreter was found after bootstrap."
}

$mainArgs = @("main.py", "--auto-launch", "--port", $Port.ToString())
if ($CpuOnly) {
    $mainArgs += "--cpu"
}

if ($SafeMode -or $WhitelistCustomNodes.Count -gt 0) {
    if ($WhitelistCustomNodes.Count -gt 0) {
        Write-Host "Launching ARM safe mode with whitelisted custom nodes: $($WhitelistCustomNodes -join ', ')"
    } else {
        Write-Host "Launching ARM safe mode (custom nodes disabled)."
    }
    $mainArgs += "--disable-all-custom-nodes"
    $mainArgs += "--offline"
    if ($WhitelistCustomNodes.Count -gt 0) {
        $mainArgs += "--whitelist-custom-nodes"
        $mainArgs += $WhitelistCustomNodes
    }
}

Invoke-ArmPython -Invoker $python -Arguments $mainArgs
