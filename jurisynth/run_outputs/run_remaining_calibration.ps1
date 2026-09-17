param([int]$StructuredSmokeProcessId)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'C:\Users\Roxas\OneDrive\Desktop\Project_Space'
$JurisynthRuntime = '.\.venv-py312\Scripts\python.exe'
$env:JURISYNTH_ER_INDEX_MODE = 'sharded'
$env:JURISYNTH_ER_SHARD_COUNT = '4'
$env:PYTHONUTF8 = '1'
function Invoke-CalibrationStage {
    param([string]$Stage, [string]$Arguments)
    $JurisynthAvailable = & $JurisynthRuntime -c 'import psutil; print(psutil.virtual_memory().available/1024**3)'
    if ([double]$JurisynthAvailable -lt 5.5) { throw "Insufficient RAM before $Stage; stopped safely." }
    Write-Output "Starting $Stage"
    $JurisynthChild = Start-Process -FilePath $JurisynthRuntime -ArgumentList $Arguments -WindowStyle Hidden `
        -RedirectStandardOutput "jurisynth/run_outputs/$Stage.out.log" `
        -RedirectStandardError "jurisynth/run_outputs/$Stage.err.log" -PassThru -Wait
    if ($JurisynthChild.ExitCode -ne 0) { throw "$Stage failed; inspect logs before continuing." }
    Write-Output "Finished $Stage"
}
foreach ($JurisynthVariant in @('A', 'B', 'C')) {
    $JurisynthCap = if ($JurisynthVariant -eq 'C') { 100 } else { 50 }
    $JurisynthExpansion = if ($JurisynthVariant -eq 'B') { ' --path-expansion' } else { '' }
    $JurisynthTag = "retrieval_ablation_$JurisynthVariant"
    Invoke-CalibrationStage -Stage $JurisynthTag -Arguments `
        "-m jurisynth.run_global_assertion_evaluation --case-file jurisynth/evaluation_artifacts/retrieval_ablation/development_cases.jsonl --run-tag $JurisynthTag --max-quads-per-seed $JurisynthCap --record-pool --output-dir jurisynth/evaluation_artifacts/retrieval_ablation$JurisynthExpansion"
    $JurisynthSummary = Get-Content -LiteralPath "jurisynth/evaluation_artifacts/retrieval_ablation/${JurisynthTag}_summary.json" -Raw | ConvertFrom-Json
    if ($JurisynthSummary.error_count -gt 0) { throw "$JurisynthTag reported errors; stopping comparison." }
}
Wait-Process -Id $StructuredSmokeProcessId -ErrorAction SilentlyContinue
$JurisynthFormatSmoke = Get-Content -LiteralPath 'jurisynth/run_outputs/structured_output_smoke_v1.json' -Raw | ConvertFrom-Json
if ($JurisynthFormatSmoke.status -ne 'success') { throw 'Structured-output smoke did not pass; global retries are gated.' }
foreach ($JurisynthQueryVariant in @('messy', 'organized')) {
    Invoke-CalibrationStage -Stage "global_complex_${JurisynthQueryVariant}_v6" -Arguments `
        "-m jurisynth.run_global_smoke --query-file jurisynth/evaluation_artifacts/complex_ai_medical_$JurisynthQueryVariant.txt --minimum-available-gb 5.5 --output jurisynth/run_outputs/global_complex_ai_medical_${JurisynthQueryVariant}_bounded_v6.json"
}
Write-Output 'Queue complete. JSON artifacts still require quality review; defaults were not changed.'
