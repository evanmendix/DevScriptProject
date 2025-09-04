<#
.SYNOPSIS
  Control laptop internal display brightness via WMI/CIM.

.DESCRIPTION
  Provides four operations:
    -Get                Prints current brightness (0-100)
    -Set <0-100>        Sets brightness to an absolute value
    -Inc [step]         Increases brightness by step (default 5)
    -Dec [step]         Decreases brightness by step (default 5)

  This script targets the internal (integrated) display only, using:
    - root\wmi: WmiMonitorBrightness (read)
    - root\wmi: WmiMonitorBrightnessMethods (write)

  External monitors typically do not support these WMI classes.

.PARAMETER Get
  Query current brightness.

.PARAMETER Set
  Absolute brightness value (0-100).

.PARAMETER Inc
  Step value to increase brightness (default 5 when specified without value).

.PARAMETER Dec
  Step value to decrease brightness (default 5 when specified without value).

.EXAMPLES
  powershell -ExecutionPolicy Bypass -File .\brightness.ps1 -Get
  powershell -ExecutionPolicy Bypass -File .\brightness.ps1 -Set 60
  powershell -ExecutionPolicy Bypass -File .\brightness.ps1 -Inc 10
  powershell -ExecutionPolicy Bypass -File .\brightness.ps1 -Dec

.NOTES
  Requires Windows on a device with an integrated display that exposes WmiMonitor* classes.
  Should not require admin privileges on most systems.
#>
[CmdletBinding(DefaultParameterSetName='Get')]
param(
  [Parameter(ParameterSetName='Get', Mandatory = $false)]
  [switch]$Get,

  [Parameter(ParameterSetName='Set', Mandatory = $true)]
  [ValidateRange(0,100)]
  [int]$Set,

  [Parameter(ParameterSetName='Inc', Mandatory = $false)]
  [ValidateRange(1,100)]
  [int]$Inc,

  [Parameter(ParameterSetName='Dec', Mandatory = $false)]
  [ValidateRange(1,100)]
  [int]$Dec
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-InternalDisplayCimObjects {
  param()
  # Filter to active monitors; these classes only exist for internal displays typically.
  $brightness = Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightness -ErrorAction Stop |
                Where-Object { $_.Active -eq $true }
  $methods    = Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightnessMethods -ErrorAction Stop |
                Where-Object { $_.InstanceName -and $_.InstanceName -match 'DISPLAY' }

  if (-not $brightness) {
    throw 'No active internal display found (WmiMonitorBrightness). This feature may not be supported on this device or display.'
  }
  if (-not $methods) {
    throw 'No internal display methods found (WmiMonitorBrightnessMethods). Unable to set brightness on this device.'
  }

  # Try to pair objects by InstanceName when possible; otherwise use the first of each.
  foreach ($b in $brightness) {
    $match = $methods | Where-Object { $_.InstanceName -eq $b.InstanceName }
    if ($match) {
      return [PSCustomObject]@{ BrightnessObj = $b; MethodsObj = $match | Select-Object -First 1 }
    }
  }

  # Fallback to the first available pair.
  return [PSCustomObject]@{ BrightnessObj = $brightness | Select-Object -First 1; MethodsObj = $methods | Select-Object -First 1 }
}

function Get-CurrentBrightness {
  param()
  $pair = Get-InternalDisplayCimObjects
  return [int]$pair.BrightnessObj.CurrentBrightness
}

function Clamp {
  param(
    [Parameter(Mandatory)] [int]$Value,
    [int]$Min = 0,
    [int]$Max = 100
  )
  if ($Value -lt $Min) { return $Min }
  if ($Value -gt $Max) { return $Max }
  return $Value
}

function Set-Brightness {
  param(
    [Parameter(Mandatory)] [ValidateRange(0,100)] [int]$Value
  )
  $pair = Get-InternalDisplayCimObjects
  $valueClamped = Clamp -Value $Value
  # Timeout of 0 (immediate). Method signature: WmiSetBrightness(uint32 Timeout, uint8 Brightness)
  $null = Invoke-CimMethod -InputObject $pair.MethodsObj -MethodName WmiSetBrightness -Arguments @{ Timeout = 0; Brightness = [byte]$valueClamped }
  return $valueClamped
}

function Increase-Brightness {
  param(
    [int]$Step = 5
  )
  $current = Get-CurrentBrightness
  $target  = Clamp -Value ($current + $Step)
  Set-Brightness -Value $target | Out-Null
  return $target
}

function Decrease-Brightness {
  param(
    [int]$Step = 5
  )
  $current = Get-CurrentBrightness
  $target  = Clamp -Value ($current - $Step)
  Set-Brightness -Value $target | Out-Null
  return $target
}

try {
  switch ($PSCmdlet.ParameterSetName) {
    'Get' {
      $val = Get-CurrentBrightness
      Write-Output $val
    }
    'Set' {
      $val = Set-Brightness -Value $Set
      Write-Output $val
    }
    'Inc' {
      if (-not $PSBoundParameters.ContainsKey('Inc')) { $Inc = 5 }
      $val = Increase-Brightness -Step $Inc
      Write-Output $val
    }
    'Dec' {
      if (-not $PSBoundParameters.ContainsKey('Dec')) { $Dec = 5 }
      $val = Decrease-Brightness -Step $Dec
      Write-Output $val
    }
    default {
      throw 'Unexpected parameter set.'
    }
  }
}
catch {
  Write-Error $_.Exception.Message
  exit 1
}
