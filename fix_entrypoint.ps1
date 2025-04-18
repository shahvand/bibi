$content = Get-Content -Raw -Path "docker-entrypoint.sh"
$content = $content -replace "`r`n", "`n"
[System.IO.File]::WriteAllText("docker-entrypoint.sh", $content) 