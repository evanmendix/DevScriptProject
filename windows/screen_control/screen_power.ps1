<#
.SYNOPSIS
  Turn the internal display on or off using Windows messages.

.DESCRIPTION
  Uses User32::SendMessage (WM_SYSCOMMAND/SC_MONITORPOWER) to control monitor power state.
  -On  : Wake/turn on the display (also performs a tiny mouse jiggle as a fallback)
  -Dim : Soft off / low-power state (often easier to wake, closer to system behavior)
  -Off : Force off (may cause issues on some laptops)

.PARAMETER On
  Turn the display on.

.PARAMETER Dim
  Put display into a low-power state (lParam=1). Often preferable to avoid wake issues.

.PARAMETER Off
  Turn the display off.

.EXAMPLES
  powershell -ExecutionPolicy Bypass -File .\screen_power.ps1 -On
  powershell -ExecutionPolicy Bypass -File .\screen_power.ps1 -Dim
  powershell -ExecutionPolicy Bypass -File .\screen_power.ps1 -Off
#>
[CmdletBinding(DefaultParameterSetName='On')]
param(
  [Parameter(ParameterSetName='On')]
  [switch]$On,

  [Parameter(ParameterSetName='Dim')]
  [switch]$Dim,

  [Parameter(ParameterSetName='Off')]
  [switch]$Off
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

namespace Win32 {
    public static class NativeMethods {
        public const int HWND_BROADCAST = 0xFFFF;
        public const int WM_SYSCOMMAND  = 0x0112;
        public const int SC_MONITORPOWER = 0xF170;

        [DllImport("user32.dll", SetLastError=false)]
        public static extern IntPtr SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll", SetLastError=false)]
        public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
        public const uint MOUSEEVENTF_MOVE = 0x0001;
    }
}
"@

function Invoke-MonitorPower {
  param(
    [Parameter(Mandatory)] [ValidateSet('On','Off')] [string]$State
  )
  if ($State -eq 'Off') {
    $lparam = [IntPtr]2   # 2 = power off
  } else {
    $lparam = [IntPtr](-1) # -1 = power on
  }
  [void][Win32.NativeMethods]::SendMessage([IntPtr][Win32.NativeMethods]::HWND_BROADCAST,
                                           [Win32.NativeMethods]::WM_SYSCOMMAND,
                                           [IntPtr][Win32.NativeMethods]::SC_MONITORPOWER,
                                           $lparam)
}

try {
  switch ($PSCmdlet.ParameterSetName) {
    'Off' {
      Invoke-MonitorPower -State 'Off'
      return
    }
    'Dim' {
      # Use lParam=1 (low power). Implemented via On path with special lParam.
      # We reuse Invoke-MonitorPower by sending lParam ourselves here.
      [void][Win32.NativeMethods]::SendMessage([IntPtr][Win32.NativeMethods]::HWND_BROADCAST,
                                               [Win32.NativeMethods]::WM_SYSCOMMAND,
                                               [IntPtr][Win32.NativeMethods]::SC_MONITORPOWER,
                                               [IntPtr]1)
      return
    }
    'On' {
      Invoke-MonitorPower -State 'On'
      # Fallback: small mouse jiggle to ensure wake
      [Win32.NativeMethods]::mouse_event([Win32.NativeMethods]::MOUSEEVENTF_MOVE, 1, 1, 0, [UIntPtr]::Zero)
      Start-Sleep -Milliseconds 50
      [Win32.NativeMethods]::mouse_event([Win32.NativeMethods]::MOUSEEVENTF_MOVE, 0, 0, 0, [UIntPtr]::Zero)
      return
    }
    default { throw 'Unexpected parameter set.' }
  }
}
catch {
  Write-Error $_.Exception.Message
  exit 1
}
