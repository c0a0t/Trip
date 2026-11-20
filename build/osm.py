"""构建期用的 OSM 服务小工具：Nominatim / Overpass / OSRM（FOSSGIS），带 UA、限速和重试。"""
import json, math, time, urllib.parse, urllib.request

UA = "sydney-trip-map-build/1.0 (one-off personal itinerary map; low volume)"
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.private.coffee/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
_last = {}

def _throttle(key, gap):
    t = _last.get(key, 0); now = time.time()
    if now - t < gap: time.sleep(gap - (now - t))
    _last[key] = time.time()

def get(url, data=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def overpass(q, tries=3):
    body = urllib.parse.urlencode({"data": "[out:json][timeout:90];" + q}).encode()
    err = None
    for i in range(tries):
        for ep in OVERPASS:
            try:
                _throttle("overpass", 2)
                return get(ep, body, timeout=120)["elements"]
            except Exception as e:
                err = e; print("   overpass retry:", ep.split("/")[2], e)
        time.sleep(5)
    raise RuntimeError(f"overpass failed: {err}")

def nominatim(**params):
    params.update(format="jsonv2", limit=3, countrycodes="au")
    _throttle("nominatim", 1.2)
    return get("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params))

def osrm(profile, pts, **extra):
    """profile: 'foot' | 'car'。pts: [(lat,lng),...]。返回 OSRM route 对象（geojson 几何，含 steps）。"""
    coords = ";".join(f"{lng:.6f},{lat:.6f}" for lat, lng in pts)
    params = dict(overview="full", geometries="geojson", steps="true")
    params.update(extra)
    url = f"https://routing.openstreetmap.de/routed-{profile}/route/v1/driving/{coords}?" + urllib.parse.urlencode(params)
    for i in range(4):
        try:
            _throttle("osrm", 1.1)
            res = get(url, timeout=60)
            if res.get("code") == "Ok": return res["routes"][0]
            raise RuntimeError(res.get("code"))
        except Exception as e:
            print("   osrm retry:", e); time.sleep(3)
    raise RuntimeError("osrm failed " + url)

def hav(a, b):
    R = 6371000.0; r = math.pi / 180
    dl = (b[0] - a[0]) * r; do = (b[1] - a[1]) * r
    h = math.sin(dl / 2) ** 2 + math.cos(a[0] * r) * math.cos(b[0] * r) * math.sin(do / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def length(path):
    return sum(hav(path[i - 1], path[i]) for i in range(1, len(path)))
