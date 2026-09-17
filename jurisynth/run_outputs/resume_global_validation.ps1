param([int]$PreviousProcessId)

$ErrorActionPreference = 'Stop'
$JurisynthWorkspace = 'C:\Users\Roxas\OneDrive\Desktop\Project_Space'
Set-Location -LiteralPath $JurisynthWorkspace
$JurisynthRuntime = Join-Path $JurisynthWorkspace '.venv-py312\Scripts\python.exe'
$env:JURISYNTH_ER_INDEX_MODE = 'sharded'
$env:JURISYNTH_ER_SHARD_COUNT = '4'
$env:PYTHONUTF8 = '1'
if ($PreviousProcessId -gt 0) {
    Wait-Process -Id $PreviousProcessId -ErrorAction SilentlyContinue
}

function Invoke-JurisynthValidation {
    param([string]$Stage, [string]$Arguments)
    $JurisynthAvailable = & $JurisynthRuntime -c 'import psutil; print(psutil.virtual_memory().available/1024**3)'
    if ([double]$JurisynthAvailable -lt 5.5) {
        throw "Insufficient available RAM for $Stage; stopped safely before loading global artifacts."
    }
    Write-Output "Starting $Stage"
    $JurisynthChild = Start-Process -FilePath $JurisynthRuntime -ArgumentList $Arguments `
        -WindowStyle Hidden -RedirectStandardOutput "jurisynth/run_outputs/$Stage.out.log" `
        -RedirectStandardError "jurisynth/run_outputs/$Stage.err.log" -PassThru -Wait
    if ($JurisynthChild.ExitCode -ne 0) {
        throw "$Stage exited with code $($JurisynthChild.ExitCode); inspect its logs."
    }
    Write-Output "Finished $Stage"
}

Invoke-JurisynthValidation -Stage 'global_complex_messy_v5' -Arguments `
    '-m jurisynth.run_global_smoke --query-file jurisynth/evaluation_artifacts/complex_ai_medical_messy.txt --minimum-available-gb 5.5 --output jurisynth/run_outputs/global_complex_ai_medical_messy_bounded_v5.json'

Invoke-JurisynthValidation -Stage 'global_assertion_stratified_probe_v2' -Arguments `
    '-m jurisynth.run_global_assertion_evaluation --sample-mode batch-stratified --limit 2'
$JurisynthProbe = Get-Content -LiteralPath 'jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_2_v2_summary.json' -Raw | ConvertFrom-Json
if ($JurisynthProbe.error_count -ne 0) {
    throw 'The two-case assertion probe reported retrieval errors; stopped before the 200-case run.'
}
Invoke-JurisynthValidation -Stage 'global_assertion_stratified_200_v2' -Arguments `
    '-m jurisynth.run_global_assertion_evaluation --sample-mode batch-stratified --limit 200'
Write-Output 'Queue completed. Inspect JSON results; process completion is not a legal-quality verdict.'
