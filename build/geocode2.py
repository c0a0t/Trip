"""第二轮地理编码：对第一轮没查到 / 精度不够的地点换查询词或用 Overpass 查精确要素。
Nominatim 每秒不超过 1 次（这里 1.2 s），带 User-Agent。结果写入 build/geocode-refine.json。"""
import json, math, time, urllib.parse, urllib.request, pathlib

HERE = pathlib.Path(__file__).parent
UA = "sydney-trip-map-build/1.0 (one-off personal itinerary map; low volume)"

def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def nomi(**params):
    params.update(format="jsonv2", limit=3, countrycodes="au")
    res = get("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params))
    time.sleep(1.2)
    return [(float(x["lat"]), float(x["lon"]), x["display_name"][:100], x.get("category", "") + "/" + x.get("type", "")) for x in res]

def overpass(q):
    data = urllib.parse.urlencode({"data": "[out:json][timeout:60];" + q}).encode()
    for ep in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        try:
            res = get(ep, data)
            time.sleep(2)
            return res["elements"]
        except Exception as e:
            print("  overpass fail", ep, e)
    return []

QUERIES = {
    "home":         [dict(street="89 Bay Street", city="Glebe", postalcode="2037"), dict(q="89 Bay Street, Glebe")],
    "dh":           [dict(q="Tumbalong Park")],
    "hpb":          [dict(q="Hyde Park Barracks")],
    "hydepark":     [dict(q="Archibald Fountain, Sydney"), dict(q="J.F. Archibald Memorial Fountain")],
    "secretgarden": [dict(q="Wendy's Secret Garden, Lavender Bay"), dict(q="Wendy Whiteley Secret Garden")],
    "mpwharf":      [dict(q="Milsons Point Wharf"), dict(q="Milsons Point ferry")],
    "zootop":       [dict(q="Taronga Zoo, Bradleys Head Road, Mosman")],
    "glebemkt":     [dict(q="Glebe Public School"), dict(q="Glebe Markets")],
    "usyd":         [dict(q="Quadrangle, University of Sydney, Camperdown"), dict(q="Main Quadrangle University of Sydney")],
    "icebergs":     [dict(q="Bondi Icebergs, Notts Avenue"), dict(q="Icebergs Bondi")],
    "echopoint":    [dict(q="Echo Point, Katoomba"), dict(q="Three Sisters Katoomba")],
    "cq":           [dict(q="Circular Quay Wharf"), dict(q="Circular Quay ferry wharf")],
    "airport":      [dict(q="Sydney Airport Terminal 1 International"), dict(q="Sydney Airport T2 Domestic")],
    "milsonpark":   [dict(q="Milson Park, Kirribilli")],
}

out = {}
for k, qs in QUERIES.items():
    out[k] = []
    for q in qs:
        try:
            r = nomi(**q)
        except Exception as e:
            print(k, "ERR", e); r = []
        print(f"{k:13s} {q} ->")
        for c in r:
            print(f"     {c[0]:.5f},{c[1]:.5f} [{c[3]}] {c[2]}")
        out[k].append({"q": q, "res": r})

# Overpass：住处门牌、动物园入口、渡轮码头
print("\n== Overpass: 89 Bay Street ==")
els = overpass('nwr["addr:housenumber"~"^89"]["addr:street"="Bay Street"](-33.890,151.185,-33.870,151.200);out center tags;')
for e in els:
    c = e.get("center", e)
    print(" ", e["type"], e["id"], c.get("lat"), c.get("lon"), e.get("tags"))
out["home_overpass"] = els
print("\n== Overpass: Bay Street 门牌 80-99（核对 89 号在哪一段）==")
els2 = overpass('nwr["addr:street"="Bay Street"]["addr:housenumber"](-33.890,151.185,-33.870,151.200);out center tags;')
nums = []
for e in els2:
    c = e.get("center", e)
    n = e["tags"]["addr:housenumber"]
    try: v = int("".join(ch for ch in n.split("-")[0] if ch.isdigit()))
    except ValueError: continue
    if 60 <= v <= 120:
        nums.append((v, n, c.get("lat"), c.get("lon"), e["tags"].get("addr:suburb", ""), e["tags"].get("addr:postcode", "")))
for t in sorted(nums): print(" ", t)
out["bay_numbers"] = nums
print("\n== Overpass: Taronga entrances / ferry wharves ==")
els3 = overpass('(nwr["entrance"](around:400,-33.8431,151.2412);nwr["amenity"="ferry_terminal"](-33.865,151.205,-33.840,151.245););out center tags;')
for e in els3:
    c = e.get("center", e)
    print(" ", e["type"], e["id"], c.get("lat"), c.get("lon"), {k: v for k, v in e.get("tags", {}).items() if k in ("name", "entrance", "amenity", "ref")})
out["zoo_wharf_overpass"] = els3
(HERE / "geocode-refine.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
