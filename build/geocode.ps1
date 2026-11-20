# 用 Nominatim 按 P[*].q 重新地理编码，和 data.js 里的近似 ll 对比。
# 速率：每次请求后 sleep 1.2 s（Nominatim 上限 1 次/秒），带 User-Agent。
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = Split-Path $PSScriptRoot -Parent
$src = [IO.File]::ReadAllText((Join-Path $root 'data.js'), [Text.Encoding]::UTF8)
$UA = 'sydney-trip-map-build/1.0 (one-off personal itinerary map; low volume)'

$rx = [regex]'(?m)^\s*(\w+):\{n:"([^"]*)",ll:\[([-\d.]+),([-\d.]+)\],q:"([^"]*)"'
$places = foreach ($m in $rx.Matches($src)) {
  [pscustomobject]@{ k=$m.Groups[1].Value; n=$m.Groups[2].Value; lat=[double]$m.Groups[3].Value; lng=[double]$m.Groups[4].Value; q=$m.Groups[5].Value }
}
# 额外：蓝山 Echo Point（places.csv 里有这一行，地图上作为蓝山的附属标记）
$places += [pscustomobject]@{ k='echopoint'; n='Echo Point 三姐妹峰'; lat=0; lng=0; q='Echo Point Lookout, Katoomba NSW' }

function Dist($a1,$o1,$a2,$o2){ $R=6371000; $r=[Math]::PI/180
  $dl=($a2-$a1)*$r; $do=($o2-$o1)*$r
  $h=[Math]::Sin($dl/2)*[Math]::Sin($dl/2)+[Math]::Cos($a1*$r)*[Math]::Cos($a2*$r)*[Math]::Sin($do/2)*[Math]::Sin($do/2)
  return [int](2*$R*[Math]::Asin([Math]::Sqrt($h))) }

$out = [ordered]@{}
foreach ($p in $places) {
  $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=3&countrycodes=au&addressdetails=0&q=' + [uri]::EscapeDataString($p.q)
  try { $res = Invoke-RestMethod -Uri $url -UserAgent $UA -TimeoutSec 30 } catch { $res = @(); Write-Host "ERR $($p.k): $_" }
  $cands = @($res | ForEach-Object { [ordered]@{ lat=[double]$_.lat; lng=[double]$_.lon; name=$_.display_name; cls="$($_.category)/$($_.type)" } })
  $out[$p.k] = [ordered]@{ n=$p.n; q=$p.q; old=@($p.lat,$p.lng); cands=$cands }
  if ($cands.Count) { $c=$cands[0]; $d = if($p.lat){ Dist $p.lat $p.lng $c.lat $c.lng } else { -1 }
    Write-Host ("{0,-13} {1,6} m  {2:N5},{3:N5}  [{4}] {5}" -f $p.k,$d,$c.lat,$c.lng,$c.cls,($c.name.Substring(0,[Math]::Min(90,$c.name.Length)))) }
  else { Write-Host ("{0,-13}  NO RESULT  q={1}" -f $p.k,$p.q) }
  Start-Sleep -Milliseconds 1200
}
$json = $out | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'geocode-raw.json'), $json, (New-Object Text.UTF8Encoding $false))
