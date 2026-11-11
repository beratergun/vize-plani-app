# Windows.Media.Ocr (yerleşik OCR) ile PNG listesini okur. Kullanım: powershell -File ocr_batch.ps1 <liste.txt> <cikti.json>
# liste.txt: her satır bir PNG yolu. cikti.json: { "yol": "metin", ... }
param([string]$List, [string]$Out)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Storage.StorageFile, Windows.Foundation, ContentType=WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $type) { $t = $asTask.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$res = [ordered]@{}
foreach ($p in (Get-Content -LiteralPath $List -Encoding UTF8)) {
  if (-not $p) { continue }
  try {
    $f = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($p)) ([Windows.Storage.StorageFile])
    $s = Await ($f.OpenReadAsync()) ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
    $d = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($s)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $b = Await ($d.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $r = Await ($engine.RecognizeAsync($b)) ([Windows.Media.Ocr.OcrResult])
    $res[$p] = ($r.Lines | ForEach-Object { $_.Text }) -join "`n"
  } catch { $res[$p] = "__OCR_ERR__ " + $_.Exception.Message }
}
$res | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $Out -Encoding UTF8
