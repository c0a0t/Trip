"""汇总核准后的坐标 -> ../geo.json，并打印与 data.js 原近似坐标的偏差。
坐标来源见每条的 src（Nominatim 搜索结果 / Overpass 要素 / 门牌插值）。查询过程见 geocode*.py 和 bay_*.py。"""
import json, pathlib, re
import osm

ROOT = pathlib.Path(__file__).resolve().parent.parent
FINAL = {
 "home":        (-33.88075, 151.19458, "门牌插值：OSM 无 89 号门牌点。Bay St 西侧（Glebe 侧）1 号=Broadway 购物中心(南端)、77/79 号在 Queen St 口(-33.8813)，号码往北递增；89 号取 Queen St–Wentworth St 之间西侧，误差约 ±40 m"),
 "fish":        (-33.87438, 151.19067, "Nominatim: Sydney Fish Market, 1 Bridge Rd (marketplace)"),
 "broadway":    (-33.88369, 151.19388, "Nominatim: Broadway Shopping Centre, 1 Bay St"),
 "dh":          (-33.87568, 151.20172, "Nominatim: Tumbalong Park"),
 "barangaroo":  (-33.85849, 151.20116, "Nominatim: Barangaroo Reserve"),
 "dawes":       (-33.85525, 151.20919, "Nominatim: Dawes Point Reserve"),
 "cq":          (-33.86090, 151.21100, "Overpass: Circular Quay 4 号码头（2B–6B 码头节点中间）"),
 "soh":         (-33.85720, 151.21512, "Nominatim: Sydney Opera House"),
 "rbg":         (-33.86277, 151.21571, "Nominatim: Royal Botanic Garden（园区中心）"),
 "hpb":         (-33.86962, 151.21280, "Nominatim: Hyde Park Barracks (museum)"),
 "stmary":      (-33.87124, 151.21336, "Nominatim: St Mary's Cathedral"),
 "hydepark":    (-33.87097, 151.21180, "Nominatim: Archibald Fountain"),
 "westfield":   (-33.87015, 151.20890, "Nominatim: Westfield Sydney, Pitt Street Mall"),
 "stjames":     (-33.87123, 151.21177, "Nominatim: St James station"),
 "cqstn":       (-33.86136, 151.21072, "Nominatim: Circular Quay station"),
 "rocks":       (-33.85999, 151.20832, "Nominatim: The Rocks（街区中心）"),
 "obs":         (-33.85976, 151.20534, "Nominatim: Observatory Hill Park"),
 "bstairs":     (-33.85912, 151.20698, "Nominatim: The Bridge Stairs, Cumberland St"),
 "milsonspt":   (-33.84665, 151.21273, "Nominatim: Milsons Point Station"),
 "milsonpark":  (-33.84417, 151.21438, "Nominatim: Milson Park, McDougall Street"),
 "secretgarden":(-33.84401, 151.20868, "Nominatim: Wendy Whiteley's Garden"),
 "mpwharf":     (-33.84959, 151.21086, "Nominatim/Overpass: Milsons Point Wharf (ferry_terminal)"),
 "zoowharf":    (-33.84639, 151.23960, "Nominatim/Overpass: Taronga Zoo ferry terminal"),
 "zootop":      (-33.84245, 151.24162, "Overpass: 动物园 entrance=main（Bradleys Head Rd 正门）"),
 "meet":        (-33.88144, 151.20445, "Nominatim: Haymarket（示例位置，以团为准）"),
 "bluemtn":     (-33.72895, 150.30126, "Nominatim: Scenic World, Katoomba"),
 "echopoint":   (-33.73224, 150.31217, "Nominatim: Echo Point, Katoomba（蓝山附属标记）"),
 "chinatown":   (-33.87815, 151.20402, "Nominatim: Dixon Street (pedestrian)"),
 "paddys":      (-33.87985, 151.20344, "Nominatim: Paddy's Markets, 9-13 Hay St"),
 "glebemkt":    (-33.88353, 151.19088, "Nominatim: Glebe Public School（市集所在）"),
 "usyd":        (-33.88591, 151.18879, "Overpass: The Quadrangle, University of Sydney"),
 "ashmore":     (-33.90277, 151.18918, "Nominatim: Ashmore Street, Erskineville"),
 "happypho":    (-33.90914, 151.22365, "Nominatim: Happy Pho, Anzac Parade, Kensington (restaurant)"),
 "bondi":       (-33.89237, 151.27808, "Overpass: Bondi Beach (natural=beach)"),
 "icebergs":    (-33.89505, 151.27457, "Nominatim: Bondi Icebergs Pool, Notts Ave"),
 "glebepointrd":(-33.88031, 151.18739, "Nominatim: Glebe Point Road（街道中心）"),
 "airport":     (-33.93626, 151.16448, "Nominatim: Sydney Airport T1 International（国际航站楼；国内航班请改 T2/T3）"),
}

src = (ROOT / "data.js").read_text(encoding="utf-8")
old = {m[0]: (float(m[1]), float(m[2])) for m in re.findall(r'(?m)^\s*(\w+):\{n:"[^"]*",ll:\[([-\d.]+),([-\d.]+)\]', src)}
print(f"{'key':13s} {'偏差(m)':>8s}  新坐标")
rows = []
for k, (la, ln, s) in FINAL.items():
    d = round(osm.hav(old[k], (la, ln))) if k in old else None
    rows.append((k, d))
    print(f"{k:13s} {str(d) if d is not None else '-':>8s}  {la:.5f},{ln:.5f}  {s[:60]}")
missing = set(old) - set(FINAL)
assert not missing, missing
geo = {k: {"ll": [la, ln], "src": s} for k, (la, ln, s) in FINAL.items()}
(ROOT / "geo.json").write_text(json.dumps(geo, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n偏差 > 150 m 的（已人工复核）：", [r for r in rows if r[1] and r[1] > 150])
