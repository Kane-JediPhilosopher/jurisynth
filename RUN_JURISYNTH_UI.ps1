param(
    [switch]$CheckOnly,
    [switch]$NoBrowser,
    [switch]$SmokeTest,
    [int]$StartupSeconds = 240
)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskFrontend = Join-Path $taskRoot 'jurisynth\frontend\stitch_research_dossier'
$taskVite = Join-Path $taskFrontend 'node_modules\vite\bin\vite.js'
$taskPython = Join-Path $taskRoot '.venv-py312\Scripts\python.exe'
$taskDotenv = Join-Path $taskRoot 'jurisynth\agentic_reasoner\.env'
$taskBackendUrl = 'http://127.0.0.1:8000/api/v1/health'
$taskFrontendUrl = 'http://127.0.0.1:3000'
$taskOwned = @()

function Assert-PortFree([int]$TaskPort) {
    $taskClient = [System.Net.Sockets.TcpClient]::new()
    try {
        $taskConnection = $taskClient.ConnectAsync('127.0.0.1', $TaskPort)
        if ($taskConnection.Wait(500) -and $taskClient.Connected) {
            throw "Port $TaskPort is already occupied. Close your previous Jurisynth launcher/service; this launcher will not kill an unknown process."
        }
    } catch [System.AggregateException] {
        # Refused connection: expected when the port is free.
    } finally { $taskClient.Dispose() }
}

function Wait-LocalService([string]$TaskUrl, $TaskProcess, [int]$TaskBudget) {
    $taskDeadline = (Get-Date).AddSeconds($TaskBudget)
    while ((Get-Date) -lt $taskDeadline) {
        $TaskProcess.Refresh()
        if ($TaskProcess.HasExited) { throw "A Jurisynth service exited during startup. See the printed log directory." }
        try {
            $taskResponse = Invoke-WebRequest -Uri $TaskUrl -TimeoutSec 2 -UseBasicParsing
            if ($taskResponse.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    throw "Service startup exceeded $TaskBudget seconds: $TaskUrl. This is a launcher startup check, not a query/NIM timeout."
}

function Stop-OwnedService($TaskProcess) {
    $TaskProcess.Refresh()
    if ($TaskProcess.HasExited) { return }
    # The venv launcher may spawn its base Python executable. Resolve only
    # descendants of the process started by this launcher, never all Python.
    $taskDescendants = @()
    $taskPending = @($TaskProcess.Id)
    while ($taskPending.Count -gt 0) {
        $taskNext = @()
        foreach ($taskParent in $taskPending) {
            foreach ($taskChild in @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $taskParent" -ErrorAction SilentlyContinue)) {
                if ($taskChild.CreationDate -ge $TaskProcess.StartTime) {
                    $taskDescendants += $taskChild.ProcessId
                    $taskNext += $taskChild.ProcessId
                }
            }
        }
        $taskPending = $taskNext
    }
    [array]::Reverse($taskDescendants)
    foreach ($taskChildId in $taskDescendants) { Stop-Process -Id $taskChildId -Force -ErrorAction SilentlyContinue }
    $TaskProcess.Refresh()
    if (-not $TaskProcess.HasExited) { Stop-Process -Id $TaskProcess.Id -Force -ErrorAction SilentlyContinue }
}

try {
    if ($StartupSeconds -lt 1) { throw 'StartupSeconds must be positive.' }
    foreach ($taskRequired in @($taskPython, $taskVite, $taskDotenv)) {
        if (-not (Test-Path -LiteralPath $taskRequired -PathType Leaf)) { throw "Missing required file: $taskRequired. Use the existing Python environment and install the frontend dependencies; this launcher does not install anything automatically." }
    }
    $taskNodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
    if ($null -eq $taskNodeCommand) { throw 'Node.js is not on PATH. Install/enable Node.js before launching the existing React UI.' }
    $taskNode = $taskNodeCommand.Source
    $taskCheckCode = 'import sys,importlib.util; assert sys.version_info[:2]==(3,12), "Use the existing Python 3.12 environment"; required=["fastapi","uvicorn","dotenv","openai","sentence_transformers","faiss","pyoxigraph","rdflib","psutil"]; missing=[m for m in required if importlib.util.find_spec(m) is None]; assert not missing, "Missing backend dependencies: "+", ".join(missing); from dotenv import load_dotenv; load_dotenv(sys.argv[1], override=False); import os; assert os.getenv("JURISYNTH_NIM_API_KEY") and os.getenv("JURISYNTH_NIM_BASE_URL"), "The Reasoner .env needs JURISYNTH_NIM_API_KEY and JURISYNTH_NIM_BASE_URL"; print("Python 3.12/dependency/environment checks passed; no API calls.")'
    & $taskPython -c $taskCheckCode $taskDotenv
    if ($LASTEXITCODE -ne 0) { throw 'Backend preflight failed. Correct the message above; no services were started.' }
    Write-Host "Existing UI: React/Vite at $taskFrontend"
    Write-Host "Backend: jurisynth.server:app (existing pilot default; global only if JURISYNTH_WORKFLOW_SCOPE is explicitly set)."
    Write-Host "Interface: $taskFrontendUrl ; API: http://127.0.0.1:8000"
    Write-Host 'Submitting a question makes NIM calls. Starting this launcher does not submit a question, run an eval, or load the full KG.'
    if ($CheckOnly) { return }
    Assert-PortFree 8000
    Assert-PortFree 3000
    $taskStamp = (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0,6)
    $taskLogs = Join-Path $taskRoot ('jurisynth\run_outputs\ui_launcher_' + $taskStamp)
    New-Item -ItemType Directory -Path $taskLogs | Out-Null
    Write-Host "Startup logs: $taskLogs"
    $taskBackend = Start-Process -FilePath $taskPython -ArgumentList @('-m','uvicorn','jurisynth.server:app','--host','127.0.0.1','--port','8000') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskLogs 'backend.stdout.log') -RedirectStandardError (Join-Path $taskLogs 'backend.stderr.log')
    $taskOwned += $taskBackend
    Wait-LocalService $taskBackendUrl $taskBackend $StartupSeconds
    $taskPreviousApiBase = $env:VITE_JURISYNTH_API_BASE
    try {
        $env:VITE_JURISYNTH_API_BASE = 'http://127.0.0.1:8000'
        $taskUi = Start-Process -FilePath $taskNode -ArgumentList @(('"' + $taskVite + '"'),'--host','127.0.0.1','--port','3000','--strictPort') -WorkingDirectory $taskFrontend -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskLogs 'frontend.stdout.log') -RedirectStandardError (Join-Path $taskLogs 'frontend.stderr.log')
    } finally { $env:VITE_JURISYNTH_API_BASE = $taskPreviousApiBase }
    $taskOwned += $taskUi
    Wait-LocalService $taskFrontendUrl $taskUi $StartupSeconds
    $taskHealth = Invoke-RestMethod -Uri $taskBackendUrl -TimeoutSec 5
    if ($taskHealth.status -ne 'ok' -or -not $taskHealth.live_query_enabled) { throw 'The health endpoint does not identify a live-query-enabled Jurisynth API.' }
    Write-Host "Jurisynth is ready at $taskFrontendUrl"
    if ($SmokeTest) {
        Write-Host 'Launcher smoke passed: API health + frontend HTTP 200. No POST, NIM or model/graph query was executed.'
        return
    }
    if (-not $NoBrowser) { Start-Process -FilePath $taskFrontendUrl | Out-Null }
    Write-Host 'Keep this launcher open. Press Ctrl+C to stop the services it started.'
    while ($true) {
        foreach ($taskService in $taskOwned) {
            $taskService.Refresh()
            if ($taskService.HasExited) { throw 'A Jurisynth service stopped. See the startup logs.' }
        }
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ('Jurisynth launcher: ' + $_.Exception.Message) -ForegroundColor Red
    if ($taskLogs) { Write-Host "Check backend.stderr.log/frontend.stderr.log in $taskLogs" }
    exit 1
} finally {
    foreach ($taskService in $taskOwned) { Stop-OwnedService $taskService }
}
