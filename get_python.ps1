# Find a Python 3.10+ on this machine, and install one if there is none.
#
# Prints the path of a usable interpreter on stdout and nothing else, so the
# caller can capture it. Everything it has to say goes to the host instead.
#
# A brand new Windows has no Python at all, and typing `python` there opens
# the Microsoft Store rather than installing anything -- so telling the reader
# to "install Python first" is a dead end for the person this tool is for.
#
# No administrator rights are used or asked for: winget with --scope user
# first, then the python.org installer with InstallAllUsers=0. That pair is
# what the main project's setup.ps1 settled on after being run on real
# machines, and this is the same approach kept small enough to stand alone.
#
# ASCII only, deliberately: this file is invoked from a .cmd whose console
# reads the system codepage, and it has no need of anything else.

$ErrorActionPreference = "Stop"
$WANT = "3.12"
function Say($m) { Write-Host "  $m" }

function Get-Usable {
    # Every place a Python can hide, including the ones not on PATH -- winget
    # installs one and the PATH of the process already running does not learn
    # about it until it restarts.
    $seen = New-Object System.Collections.Generic.List[string]
    foreach ($cmd in @("py", "python", "python3")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) { $seen.Add($found.Source) }
    }
    $globs = @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "${env:ProgramFiles(x86)}\Python3*\python.exe"
    )
    foreach ($g in $globs) {
        Get-ChildItem $g -ErrorAction SilentlyContinue |
            ForEach-Object { $seen.Add($_.FullName) }
    }

    foreach ($exe in $seen) {
        # The Store stub lives under WindowsApps, answers every question by
        # opening a shop page, and is not a Python.
        if ($exe -like "*\WindowsApps\*") { continue }
        try {
            $args = @()
            if ([IO.Path]::GetFileName($exe) -eq "py.exe") { $args += "-3" }
            $args += @("-c", "import sys; print(sys.executable if sys.version_info >= (3,10) else '')")
            $out = (& $exe @args 2>$null | Select-Object -First 1)
            if ($out -and (Test-Path $out)) { return $out }
        } catch { }
    }
    return $null
}

$have = Get-Usable
if ($have) { Write-Output $have; exit 0 }

Say "Chua co Python 3.10+. Se cai tu dong, khong can quyen Administrator."

# --- winget, per user
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Say "thu winget install Python.Python.$WANT --scope user"
    # Out-Host: winget is chatty, and its chatter must not reach the caller
    # that is reading stdout for a path.
    & winget install --id "Python.Python.$WANT" --exact --source winget `
        --scope user --silent --disable-interactivity `
        --accept-package-agreements --accept-source-agreements 2>&1 | Out-Host
    $have = Get-Usable
    if ($have) { Write-Output $have; exit 0 }
    Say "winget khong cai duoc (exit $LASTEXITCODE), thu python.org"
} else {
    Say "may nay khong co winget, thu python.org"
}

# --- python.org, per user
try {
    # PowerShell 5.1 still offers TLS 1.0 first, which python.org refuses.
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Say "hoi python.org ban $WANT moi nhat"
    $index = Invoke-WebRequest "https://www.python.org/ftp/python/" -UseBasicParsing -TimeoutSec 60
    $versions = @($index.Links.href |
        Where-Object { $_ -match "^$([regex]::Escape($WANT))\.(\d+)/$" } |
        ForEach-Object { $_.TrimEnd('/') } |
        Sort-Object { [int]($_ -split '\.')[-1] } -Descending)
    if (-not $versions) { throw "python.org khong liet ke ban $WANT nao" }
    $suffix = if ([Environment]::Is64BitOperatingSystem) { "-amd64" } else { "" }

    # Newest is not the same as newest-with-an-installer. Once a minor version
    # goes security-only, CPython publishes source and no Windows .exe --
    # measured on 3.12, where .11 through .14 have no installer and .10 is the
    # newest that does. Taking the top of the list would 404 on every machine
    # this branch exists for, so each candidate is asked for before it is
    # committed to a 25 MB download.
    $ok = $false
    foreach ($version in $versions) {
        $url = "https://www.python.org/ftp/python/$version/python-$version$suffix.exe"
        try { $null = Invoke-WebRequest $url -Method Head -UseBasicParsing -TimeoutSec 60 }
        catch { continue }
        $exe = Join-Path $env:TEMP "python-$version$suffix.exe"
        Say "tai $version"
        Invoke-WebRequest $url -OutFile $exe -UseBasicParsing -TimeoutSec 900
        Say "cai (chi cho tai khoan nay)"
        # InstallAllUsers=0 with InstallLauncherAllUsers=0 is what keeps this
        # clear of the elevation prompt.
        $p = Start-Process $exe -Wait -PassThru -ArgumentList @(
            "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_launcher=1",
            "InstallLauncherAllUsers=0", "Include_test=0"
        )
        Remove-Item $exe -ErrorAction SilentlyContinue
        if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010) { $ok = $true }
        else { Say "bo cai bao exit $($p.ExitCode)" }
        break
    }
    if (-not $ok) { Say "khong tim duoc installer $WANT cho may nay" }
} catch {
    Say "python.org khong xong: $($_.Exception.Message)"
}

$have = Get-Usable
if ($have) { Write-Output $have; exit 0 }

Say ""
Say "Van chua co Python. Cai tay roi chay lai Install.cmd:"
Say "   winget install Python.Python.$WANT --scope user"
Say "hoac tai o python.org, khi cai tick 'Add python.exe to PATH'"
Say "va chon 'Install for me only'."
exit 1
