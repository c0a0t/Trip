"""构建期为每个路段算真实路线 -> ../routes.json（页面运行时不依赖路线服务）。
- walk  : FOSSGIS OSRM foot（routing.openstreetmap.de），部分路段加中途点贴合行程说明
- taxi / coach : 同服务 car
- bus 238 : car 路线（公交沿同一条街开），并核对经过 Athol Wharf Rd / Bradleys Head Rd
- train / lr : OSM railway 几何上做最短路
- ferry : OSM route=ferry 几何最短路；不连通时用手工水道折线；都用 OSM 海岸线校验不穿陆地
- 动物园园内步行：示意线
用法：python build/routes.py            （全部重算）
     python build/routes.py walk:bstairs>milsonpark   （只重算某段）
"""
import heapq, json, math, pathlib, re, sys
import osm

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEO = {k: tuple(v["ll"]) for k, v in json.loads((ROOT / "geo.json").read_text(encoding="utf-8")).items()}
SRC = (ROOT / "data.js").read_text(encoding="utf-8")
LEGS = []
for m in re.finditer(r'L\("(\w+)","(\w+)","(\w+)","([^"]*)"', SRC):
    k = f"{m[1]}:{m[2]}>{m[3]}"
    if k not in [x[0] for x in LEGS]: LEGS.append((k, m[1], m[2], m[3], m[4]))

# 路由锚点：有些地点正上/下方是高架路、大桥桥面或地铁站台，OSRM 会吸附到错误的层。
# 这里给出地面上的路由起止点，并用 radiuses 限制吸附半径（米）。地图标记仍在 geo.json 的位置。
ANCHOR = {
 ("foot", "dawes"):    ((-33.85602, 151.20934), 15),  # Hickson Rd 人行道（正上方是 Cahill Walk 桥面）
 ("foot", "hydepark"): ((-33.87140, 151.21240), 12),  # 海德公园北园步道（正下方是 St James 站台）
 ("car",  "soh"):      ((-33.85903, 151.21414), 10),  # 歌剧院车辆落客道（否则吸到海港隧道）
 ("car",  "cq"):       ((-33.86162, 151.21134), 10),  # Alfred St（否则吸到上方 Cahill 高速）
}
# 步行段中途点：让 OSRM 路线贴合行程说明里写的走法
WALK_VIA = {
 "walk:dh>barangaroo":    [(-33.87130, 151.20190), (-33.86790, 151.20160), (-33.86300, 151.20150)],  # Cockle Bay 东岸 → King St Wharf → Wulugul Walk
 "walk:barangaroo>dawes": [(-33.85640, 151.20420), (-33.85560, 151.20640)],   # Walsh Bay 老码头（Hickson Rd）
 "walk:rbg>hpb":          [(-33.86600, 151.21290)],                         # 出园走 Macquarie St
 "walk:rocks>obs":        [(-33.85920, 151.20720)],                         # Argyle St / Argyle Cut
 "walk:bondi>icebergs":   [(-33.89410, 151.27560)],                         # 沿海滩到南端
}
CAR_VIA = {
 "coach:meet>bluemtn": [GEO["echopoint"]],   # 团车先到 Echo Point 再去 Scenic World
}
# 瓦片上画在水面上方/上面的东西（不是陆地）：≤ 100 m 的“非水面”区段落在这些豁免区内视为正常（已目视确认）
BRIDGE_OK_M = 100
EXEMPT = [((-33.8527, 151.2099), 420, "海港大桥桥面（渡轮从桥下过）"),
          ((-33.8541, 151.2135), 70, "海港隧道 M1（瓦片在水面上画了隧道虚线）")]
def under_bridge(p):
    return any(osm.hav(p, c) <= r for c, r, _ in EXEMPT)
ZOO_SCHEMATIC =[(-33.8438, 151.2428), (-33.8452, 151.2418), (-33.8460, 151.2405)]

# 渡轮手工水道折线（OSM 渡轮几何不连通时的后备；同样要过海岸线校验）
FERRY_MANUAL = {
 # Sydney Cove 出湾 → Kirribilli Point 南侧 → Fort Denison 北侧 → Bradleys Head 西侧 → 动物园码头
 "ferry:cq>zoowharf":  [GEO["cq"], (-33.8590, 151.2112), (-33.8560, 151.2117), (-33.8540, 151.2140), (-33.8543, 151.2190),
                        (-33.8530, 151.2232), (-33.8515, 151.2330), (-33.8495, 151.2375), (-33.8475, 151.2393), GEO["zoowharf"]],
 "ferry:mpwharf>cq":   [GEO["mpwharf"], (-33.8510, 151.2112), (-33.8540, 151.2118), (-33.8570, 151.2116), (-33.8592, 151.2112), GEO["cq"]],
}

def simplify(pts, tol_m):
    if len(pts) < 3: return pts
    lat0 = math.radians(pts[0][0]); kx = 111320 * math.cos(lat0); ky = 110540
    xy = [(p[1] * kx, p[0] * ky) for p in pts]
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop(); (x1, y1), (x2, y2) = xy[a], xy[b]
        dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
        best, bi = -1, -1
        for i in range(a + 1, b):
            x, y = xy[i]
            t = 0 if L2 == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
            d = math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
            if d > best: best, bi = d, i
        if best > tol_m:
            keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]

def rnd(pts): return [[round(p[0], 5), round(p[1], 5)] for p in pts]

def osrm_leg(profile, pts, rads=None):
    extra = {"radiuses": ";".join(str(r) if r else "unlimited" for r in rads)} if rads and any(rads) else {}
    r = osm.osrm(profile, pts, **extra)
    coords = [(c[1], c[0]) for c in r["geometry"]["coordinates"]]
    names = []
    for lg in r["legs"]:
        for s in lg["steps"]:
            n = s.get("name") or s.get("ref") or ""
            if n and (not names or names[-1] != n): names.append(n)
    return coords, r["distance"], r["duration"], names

# ---------- OSM 线路图最短路（火车 / 轻轨 / 渡轮） ----------
def graph_from(q):
    els = osm.overpass(q + "out body geom;")
    adj, pos = {}, {}
    for e in els:
        if e["type"] != "way" or "geometry" not in e: continue
        ns, gs = e["nodes"], e["geometry"]
        for i, (n, g) in enumerate(zip(ns, gs)):
            if g is None: continue
            pos[n] = (g["lat"], g["lon"])
        for a, b in zip(ns, ns[1:]):
            if a in pos and b in pos:
                d = osm.hav(pos[a], pos[b])
                adj.setdefault(a, []).append((b, d)); adj.setdefault(b, []).append((a, d))
    return adj, pos

def nearest(pos, p, among=None):
    best = min((among or pos.keys()), key=lambda n: osm.hav(pos[n], p))
    return best, osm.hav(pos[best], p)

def dijkstra(adj, pos, s, t):
    dist, prev, pq = {s: 0}, {}, [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t: break
        if d > dist[u]: continue
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, 1e18): dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if t not in dist: return None
    path, u = [t], t
    while u != s: u = prev[u]; path.append(u)
    return [pos[n] for n in reversed(path)]

def biggest_component(adj, pos, p):
    """在和 p 最近的连通分量里找最近点（防止吸附到孤立的小段上）"""
    order = sorted(pos, key=lambda n: osm.hav(pos[n], p))[:80]
    return order

def rail_route(q, a, b, label):
    adj, pos = graph_from(q)
    na = [n for n in sorted(pos, key=lambda n: osm.hav(pos[n], a))[:40]]
    nb = [n for n in sorted(pos, key=lambda n: osm.hav(pos[n], b))[:40]]
    best = None
    for s in na[:12]:
        for t in nb[:12]:
            p = dijkstra(adj, pos, s, t)
            if p:
                L = osm.length(p) + osm.hav(a, p[0]) + osm.hav(p[-1], b)
                if not best or L < best[0]: best = (L, p)
        if best: break
    if not best: raise RuntimeError(f"{label}: 线路图不连通")
    print(f"   {label}: 吸附偏差 起点 {osm.hav(a, best[1][0]):.0f} m / 终点 {osm.hav(b, best[1][-1]):.0f} m")
    return best[1]

# ---------- 渡轮不能穿陆地：沿线每 15 m 取点，读 OSM 标准瓦片(z16)上该点的颜色是否为水面色 ----------
# （悉尼港在 OSM 里不是 coastline 而是 water 多边形，所以直接看渲染结果最直观；只取路线经过的十几张瓦片，带本地缓存）
TILE_CACHE = pathlib.Path(__file__).parent / "tilecache"
_tiles = {}
def _tile(z, x, y):
    from PIL import Image
    import io, urllib.request
    k = (z, x, y)
    if k not in _tiles:
        f = TILE_CACHE / f"{z}_{x}_{y}.png"
        if not f.exists():
            TILE_CACHE.mkdir(exist_ok=True)
            osm._throttle("tile", 0.5)
            req = urllib.request.Request(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png", headers={"User-Agent": osm.UA})
            f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        _tiles[k] = Image.open(f).convert("RGB")
    return _tiles[k]

def is_water(lat, lng, z=16):
    n = 2 ** z
    xf = (lng + 180) / 360 * n
    yf = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    # 瓦片上水面会画渡轮虚线和水域名称，所以看取样点周围 13×13 像素里水面色（OSM Carto #aad3df）的占比
    px, py = int(xf * 256), int(yf * 256); water = tot = 0
    for dy in range(-6, 7, 2):
        for dx in range(-6, 7, 2):
            X, Y = px + dx, py + dy
            r, g, b = _tile(z, X // 256, Y // 256).getpixel((X % 256, Y % 256))
            tot += 1; water += abs(r - 170) < 22 and abs(g - 211) < 22 and abs(b - 223) < 22
    return water / tot >= 0.3

def land_crossings(path, ignore_m=80, step=15):
    """返回不在水面上的连续区段 [(起点, 长度m)]；首尾 ignore_m 内（码头/栈桥）不计"""
    total = osm.length(path); runs = []; cur = None; d0 = 0
    for i in range(1, len(path)):
        a, b = path[i - 1], path[i]; L = osm.hav(a, b); k = max(1, int(L // step))
        for j in range(k):
            t = j / k; p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t); d = d0 + L * t
            if d < ignore_m or d > total - ignore_m: continue
            if not is_water(*p):
                if cur is None: cur = [p, d, d]
                cur[2] = d
            elif cur is not None:
                runs.append(((round(cur[0][0], 5), round(cur[0][1], 5)), round(cur[2] - cur[1] + step))); cur = None
        d0 += L
    if cur is not None: runs.append(((round(cur[0][0], 5), round(cur[0][1], 5)), round(cur[2] - cur[1] + step)))
    return runs

# ---------- 主流程 ----------
def build(key, mode, a, b, dur):
    A, B = GEO[a], GEO[b]
    info = {"mode": mode, "from": a, "to": b}
    if key == "walk:zootop>zoowharf":
        info.update(kind="schematic", coords=rnd([A, *ZOO_SCHEMATIC, B]), note="园内路线为示意")
        return info
    if mode in ("walk", "taxi", "coach", "bus"):
        prof = "foot" if mode == "walk" else "car"
        (sa, ra), (sb, rb) = ANCHOR.get((prof, a), (A, None)), ANCHOR.get((prof, b), (B, None))
        via = WALK_VIA.get(key, []) if prof == "foot" else CAR_VIA.get(key, [])
        coords, dist, secs, names = osrm_leg(prof, [sa, *via, sb], [ra, *[None] * len(via), rb])
        # 锚点和标记不重合时，用一小段直线接回标记
        if ra: coords = [A, *coords]
        if rb: coords = [*coords, B]
        if prof == "foot":
            info.update(kind="osrm-foot", dist=round(dist), names=names, coords=rnd(simplify(coords, 2.5)))
        else:
            info.update(kind="osrm-car", dist=round(dist), secs=round(secs), names=names[:40],
                        coords=rnd(simplify(coords, 25 if mode == "coach" else 4)))
    elif mode == "train":
        p = rail_route('way["railway"~"^(rail|subway)$"](-33.8760,151.2040,-33.8580,151.2160);', A, B, key)
        info.update(kind="osm-rail", dist=round(osm.length(p)), coords=rnd([A, *simplify(p, 3), B]))
    elif mode == "lr":
        p = rail_route('way["railway"="light_rail"](-33.9140,151.1990,-33.8740,151.2290);', A, B, key)
        info.update(kind="osm-light-rail", dist=round(osm.length(p)), coords=rnd([A, *simplify(p, 4), B]))
    elif mode == "ferry":
        base = key if key in FERRY_MANUAL else f"ferry:{b}>{a}"
        p, kind = None, "osm-ferry"
        try:
            p = rail_route('way["route"="ferry"](-33.866,151.200,-33.840,151.245);', A, B, key)
            if osm.length(p) > 2.2 * osm.hav(A, B) + 600: print("   OSM 渡轮最短路绕得太远，改用手工水道"); p = None
        except Exception as e:
            print("  ", e)
        if p is not None:
            p = [A, *p, B]
            bad = [r for r in land_crossings(p) if r[1] > BRIDGE_OK_M or not under_bridge(r[0])]
            if bad: print("   OSM 渡轮几何有非水面区段，改用手工水道:", bad[:3]); p = None
        if p is None:
            p = FERRY_MANUAL[base] if base == key else list(reversed(FERRY_MANUAL[base]))
            kind = "manual-waterway"
        runs = land_crossings(p)
        bad = [r for r in runs if r[1] > BRIDGE_OK_M or not under_bridge(r[0])]
        print(f"   水面校验：非水面区段 {runs or '无'}" + ("" if not bad else "  !!穿陆地"))
        info.update(kind=kind, dist=round(osm.length(p)), coords=rnd(p), water_check="ok" if not bad else bad)
    else:
        raise ValueError(mode)
    return info

def main():
    out_f = ROOT / "routes.json"
    out = json.loads(out_f.read_text(encoding="utf-8")) if out_f.exists() else {}
    only = sys.argv[1:]
    for key, mode, a, b, dur in LEGS:
        if only and key not in only: continue
        print(f"{key:28s} {dur}")
        try:
            info = build(key, mode, a, b, dur)
        except Exception as e:
            print("   !! FAILED", e); continue
        out[key] = info
        extra = f" via {' / '.join(info.get('names', [])[:8])}" if info.get("names") else ""
        print(f"   -> {info['kind']} {info.get('dist', '?')} m, {len(info['coords'])} pts{extra}")
    keys = [l[0] for l in LEGS]
    out = {k: out[k] for k in keys if k in out}
    out_f.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"\nroutes.json: {len(out)}/{len(keys)} 段, {out_f.stat().st_size // 1024} KB; 缺: {[k for k in keys if k not in out]}")

if __name__ == "__main__":
    main()
