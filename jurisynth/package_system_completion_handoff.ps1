param(
    [string]$ArchiveName = 'CHAT_SYSTEM_COMPLETION_HANDOFF_20260914.zip',
    [string]$PriorRelativePath = 'evaluation_artifacts\leaf_execution_handoff_v3\CHAT_LEAF_EXECUTION_FOLLOWUP.zip',
    [string]$OverviewName = 'CHAT_SYSTEM_COMPLETION_HANDOFF_20260914.md',
    [string]$PriorPrefix = 'prior_leaf_execution/',
    [switch]$IncludeLatencyUpdate
)
$ErrorActionPreference = 'Stop'
$taskWorkspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$taskArchivePath = Join-Path (Join-Path $PSScriptRoot 'evaluation_artifacts') $ArchiveName
if (Test-Path -LiteralPath $taskArchivePath) { throw 'Refusing to overwrite an existing hand-off archive.' }
$taskPriorArchive = Join-Path $PSScriptRoot $PriorRelativePath
$taskFiles = @{
    'THIS_HANDOFF.md' = ('jurisynth/evaluation_artifacts/' + $OverviewName)
    'COMMUNITY_AND_DEPENDENCY_REVIEW_20260914.md' = 'jurisynth/evaluation_artifacts/COMMUNITY_AND_DEPENDENCY_REVIEW_20260914.md'
    'SYSTEM_PROMPTS_20260914.md' = 'jurisynth/evaluation_artifacts/SYSTEM_PROMPTS_20260914.md'
}
$taskAdditionalFiles = @(
    'jurisynth/main.py', 'jurisynth/CHECKLIST.md',
    'jurisynth/retrieval_mech/mechanism.py', 'jurisynth/retrieval_mech/config.py',
    'jurisynth/retrieval_mech/community_selector.py', 'jurisynth/retrieval_mech/community_hierarchy.py',
    'jurisynth/retrieval_mech/community_summary.py', 'jurisynth/retrieval_mech/lazy_community_metadata.py',
    'jurisynth/agentic_reasoner/scheduler.py', 'jurisynth/agentic_reasoner/dependency_planner.py',
    'jurisynth/agentic_reasoner/schemas.py', 'jurisynth/run_live_community_smoke.py',
    'jurisynth/run_outputs/live_community_smoke.json',
    'jurisynth/to_be_built/agentic_reasoner_spec_v2.md', 'jurisynth/to_be_built/retrieval_mech_spec.md'
)
if ($IncludeLatencyUpdate) {
    $taskAdditionalFiles += @(
        'jurisynth/agentic_reasoner/llm.py', 'jurisynth/agentic_reasoner/workflow.py',
        'jurisynth/agentic_reasoner/reasoner.py', 'jurisynth/agentic_reasoner/reporting.py',
        'jurisynth/agentic_reasoner/contradiction.py', 'jurisynth/retrieval_mech/rdf_retriever.py',
        'jurisynth/retrieval_mech/er_matcher.py', 'jurisynth/retrieval_mech/er_shards.py',
        'jurisynth/retrieval_mech/rdf_store.py', 'jurisynth/retrieval_mech/image_expander.py',
        'jurisynth/retrieval_mech/query_interpreter.py', 'jurisynth/vendor/qcompiler_parser.py',
        'jurisynth/agentic_reasoner/qcompiler_translator.py', 'jurisynth/agentic_reasoner/qcompiler_adapter.py'
    )
    $taskFiles['diagnostic/diagnose_local_retrieval_latency.py'] = 'jurisynth/diagnose_local_retrieval_latency.py'
    foreach ($taskDiagnosticName in @('results.json', 'events.jsonl', 'INTERPRETATION.md')) {
        $taskFiles['diagnostic/' + $taskDiagnosticName] = 'jurisynth/run_outputs/local_latency_diagnostic_20260914_v1/' + $taskDiagnosticName
    }
}
foreach ($taskRelativePath in $taskAdditionalFiles) {
    if (Test-Path -LiteralPath (Join-Path $taskWorkspace $taskRelativePath)) {
        $taskFiles['current/' + $taskRelativePath] = $taskRelativePath
    } else { throw "Missing requested hand-off source: $taskRelativePath" }
}
$taskOldZip = [System.IO.Compression.ZipFile]::OpenRead($taskPriorArchive)
$taskNewZip = [System.IO.Compression.ZipFile]::Open($taskArchivePath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($taskOldEntry in $taskOldZip.Entries) {
        if ($taskOldEntry.FullName.EndsWith('/')) { continue }
        $taskNewEntry = $taskNewZip.CreateEntry($PriorPrefix + $taskOldEntry.FullName)
        $taskInputStream = $taskOldEntry.Open()
        $taskOutputStream = $taskNewEntry.Open()
        try { $taskInputStream.CopyTo($taskOutputStream) } finally { $taskInputStream.Dispose(); $taskOutputStream.Dispose() }
    }
    foreach ($taskEntryName in $taskFiles.Keys) {
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($taskNewZip, (Join-Path $taskWorkspace $taskFiles[$taskEntryName]), $taskEntryName) | Out-Null
    }
} finally { $taskNewZip.Dispose(); $taskOldZip.Dispose() }
$taskVerificationZip = [System.IO.Compression.ZipFile]::OpenRead($taskArchivePath)
try {
    foreach ($taskEntry in $taskVerificationZip.Entries) {
        if ($taskEntry.FullName -match '(^|/)\.env($|\.)') { throw 'Credential file detected in archive.' }
        $taskReader = [System.IO.StreamReader]::new($taskEntry.Open())
        try { if ($taskReader.ReadToEnd().Contains('nvapi-')) { throw 'API key marker detected in archive.' } } finally { $taskReader.Dispose() }
    }
    [pscustomobject]@{ Archive = $taskArchivePath; Entries = $taskVerificationZip.Entries.Count; Bytes = (Get-Item -LiteralPath $taskArchivePath).Length; SecretMarkerFound = $false }
} finally { $taskVerificationZip.Dispose() }
