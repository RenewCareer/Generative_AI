# Export each deck's slides to PNG with PowerPoint, for visual review. Usage: ./render.ps1 [deck folder filter]
param([string]$Filter = "")
$root = Split-Path $PSScriptRoot -Parent
$out = Join-Path $PSScriptRoot "_render"
$app = New-Object -ComObject PowerPoint.Application
Get-ChildItem -Path $root -Recurse -Filter presentation.pptx -Depth 3 | Where-Object { $_.FullName -notmatch 'venv|node_modules' -and $_.FullName -like "*$Filter*" } | ForEach-Object {
  $name = $_.Directory.Name
  $dir = Join-Path $out $name
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Remove-Item "$dir\*.png" -ErrorAction SilentlyContinue
  $deck = $app.Presentations.Open($_.FullName, $true, $false, $false)
  $i = 0
  foreach ($slide in $deck.Slides) { $i++; $slide.Export((Join-Path $dir ("s{0:d2}.png" -f $i)), "PNG", 1280, 720) }
  $deck.Close()
  "$name : $i slides"
}
$app.Quit()
