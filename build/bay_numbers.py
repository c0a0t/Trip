import json, urllib.parse, urllib.request
UA = "sydney-trip-map-build/1.0 (one-off personal itinerary map; low volume)"
q = '[out:json][timeout:60];(nwr["addr:street"="Bay Street"]["addr:housenumber"](-33.890,151.185,-33.870,151.200);way["name"="Bay Street"](-33.890,151.185,-33.870,151.200););out center tags;'
req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
els = json.loads(urllib.request.urlopen(req, timeout=90).read())["elements"]
rows = []
for e in els:
    c = e.get("center", e); t = e.get("tags", {})
    if "addr:housenumber" in t:
        rows.append((t["addr:housenumber"], round(c["lat"], 6), round(c["lon"], 6), t.get("addr:postcode", ""), t.get("addr:suburb", ""), t.get("name", ""), e["type"]))
    else:
        print("WAY", e["id"], c["lat"], c["lon"], t.get("highway"))
def key(r):
    s = "".join(ch for ch in r[0].split("-")[0] if ch.isdigit()); return int(s) if s else 0
for r in sorted(rows, key=key): print(r)
