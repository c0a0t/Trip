import json, time, urllib.parse, urllib.request
UA = "sydney-trip-map-build/1.0 (one-off personal itinerary map; low volume)"
def get(url, data=None):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"User-Agent": UA}), timeout=90).read())
q = '[out:json];way(148331266);out geom;way["highway"](around:60,-33.8800,151.1943);out tags;'
for e in get("https://overpass-api.de/api/interpreter", urllib.parse.urlencode({"data": q}).encode())["elements"]:
    if "geometry" in e: print("Bay St north way:", [(round(g["lat"],5), round(g["lon"],5)) for g in e["geometry"]])
    else: print("nearby way:", e["id"], e["tags"].get("highway"), e["tags"].get("name"))
for lat, lon in [(-33.8810, 151.1942), (-33.8805, 151.1942), (-33.8800, 151.1942), (-33.8795, 151.1942)]:
    time.sleep(1.2)
    r = get(f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18&lat={lat}&lon={lon}")
    print(lat, lon, "->", r.get("display_name", "")[:110])
