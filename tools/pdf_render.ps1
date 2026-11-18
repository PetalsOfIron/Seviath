# Render every page of a PDF to PNG with the built-in Windows PDF renderer.
# usage: pwsh pdf_render.ps1 <pdf> <outdir> [scale]
param([string]$Pdf, [string]$Out, [double]$Scale = 2.0)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $type) { $t = $asTask.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
function AwaitAction($op) { $m = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]; $t = $m.Invoke($null, @($op)); $t.Wait(-1) | Out-Null }
New-Item -ItemType Directory -Force $Out | Out-Null
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Pdf).Path)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
Write-Output ("pages: " + $doc.PageCount)
for ($i = 0; $i -lt $doc.PageCount; $i++) {
  $page = $doc.GetPage($i)
  $ras = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
  $opt = New-Object Windows.Data.Pdf.PdfPageRenderOptions
  $opt.DestinationWidth = [uint32]($page.Size.Width * $Scale)
  $opt.DestinationHeight = [uint32]($page.Size.Height * $Scale)
  AwaitAction ($page.RenderToStreamAsync($ras, $opt))
  $net = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($ras)
  $name = Join-Path $Out ("page_{0:000}.png" -f ($i + 1))
  $fs = [System.IO.File]::Create($name); $net.CopyTo($fs); $fs.Close(); $page.Dispose()
}
