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
 "airport":     (-33.93378, 151.17993, "Nominatim: Sydney Airport T2 Domestic（国内航站楼，T3 就在旁边；30 日飞凯恩斯是国内航班）"),
 # ---- 凯恩斯（cairns.js）；查询见 cairns_geocode.py ----
 "c_airport":   (-16.87490, 145.75222, "Overpass: Cairns Airport 航站楼（International Terminal 以南的国内航站楼）"),
 "c_home":      (-16.92075, 145.77758, "示意位置：住处待定，先放在市中心 Shields St（City Place 一带，Nominatim）"),
 "c_lagoon":    (-16.91964, 145.77798, "Nominatim: Cairns Esplanade Lagoon"),
 "c_reeffleet": (-16.92166, 145.78041, "Nominatim: Reef Fleet Terminal (ferry_terminal)"),
 "c_reef":      (-16.86800, 146.20800, "示意：Moore Reef 西缘外侧水面（OSM 礁区范围 146.212–146.252E），实际去哪片礁以团为准"),
 "c_cnsstn":    (-16.92567, 145.77126, "Nominatim: Cairns railway station, Bunda St"),
 "c_kuranda":   (-16.81848, 145.63909, "Nominatim: Kuranda railway station"),
 "c_kvillage":  (-16.81935, 145.63288, "Nominatim: Kuranda Heritage Market"),
 "c_skyk":      (-16.81913, 145.63909, "Nominatim: Skyrail Kuranda Terminal (aerialway/station)"),
 "c_skys":      (-16.84766, 145.69505, "Nominatim: Skyrail Smithfield Terminal (aerialway/station)"),
 "c_rainf":     (-16.82368, 145.65206, "Nominatim: Rainforestation Nature Park, Kennedy Hwy (tourism/zoo)"),
 "c_heli":      (-16.87172, 145.73760, "示意：Nautilus Aviation（Greenbank West Rd，凯恩斯机场西侧，Nominatim）；直升机实际降落点以商家为准"),
 "c_marina":    (-16.92140, 145.78131, "Nominatim: Marlin Marina（很多钓鱼船从这里出发；集合点待定）"),
 "c_rustys":    (-16.92444, 145.77508, "Nominatim: Rusty's Markets, 57-89 Grafton St"),
 "c_botanic":   (-16.90010, 145.75043, "Nominatim: Cairns Botanic Gardens, Collins Ave"),
 # ---- 悉尼新加的（data.js）；查询见 more_geocode.py ----
 "s_dfo":       (-33.85536, 151.07675, "Nominatim: DFO Homebush, 3-5 Underwood Rd (shop/mall)"),
 "s_mill":      (-33.91060, 151.19378, "Nominatim: 41-43 Bourke Rd, Alexandria（The Mill 里的店铺）"),
 "s_lavender":  (-33.84397, 151.20713, "Nominatim: Railway Ave, Lavender Bay（皮划艇常见集合点 1 Railway Ave 一带）"),
 "s_kayak":     (-33.85000, 151.20850, "示意：Lavender Bay 湾口外、海港大桥西侧水面（划艇路线示意）"),
 "s_bronte":    (-33.90362, 151.26829, "Nominatim: Bronte Beach (natural/beach)"),
 # ---- 阿德莱德（adelaide.js） ----
 "a_airport":   (-34.93894, 138.53750, "Nominatim/Overpass: Adelaide Airport Domestic & International Terminal"),
 "a_home":      (-34.92895, 138.59992, "示意位置：住处待定，先放在市中心 Victoria Square（Nominatim）"),
 "a_central":   (-34.93009, 138.59805, "Nominatim: Central Market Arcade"),
 "a_farmers":   (-34.94596, 138.58653, "Nominatim: Adelaide Showground, Wayville（Farmers' Market 所在）"),
 "a_rundle":    (-34.92284, 138.60260, "Nominatim: Rundle Mall (pedestrian)"),
 "a_gallery":   (-34.92063, 138.60397, "Nominatim: Art Gallery of South Australia（South Australian Museum 在旁边）"),
 "a_botanic":   (-34.91823, 138.61146, "Nominatim: Adelaide Botanic Gardens"),
 "a_river":     (-34.91958, 138.59779, "Nominatim: Adelaide Festival Centre（托伦斯河南岸）"),
 "a_penfolds":  (-34.92158, 138.67926, "Nominatim: Penfolds Magill Estate, 78 Penfold Rd"),
 # ---- 墨尔本（melbourne.js） ----
 "m_airport":   (-37.67065, 144.85030, "Nominatim: Melbourne Airport Terminal 1/2/3 Drop off"),
 "m_home":      (-37.81492, 144.96685, "示意位置：住处待定，先放在市中心 Melbourne Town Hall（Nominatim）"),
 "m_meet":      (-37.81774, 144.96916, "Nominatim: Federation Square（大洋路团集合点示例）"),
 "m_arch":      (-38.47204, 144.04458, "Nominatim: Great Ocean Road Memorial Arch"),
 "m_apollo":    (-38.75474, 143.66915, "Nominatim: Apollo Bay（镇中心）"),
 "m_12a":       (-38.66428, 143.10380, "Nominatim: The Twelve Apostles (tourism/viewpoint)"),
 "m_lochard":   (-38.64641, 143.07033, "Nominatim: Loch Ard Gorge (natural/beach)"),
 "m_flinders":  (-37.81842, 144.96648, "Nominatim: Flinders Street railway station"),
 "m_belgrave":  (-37.90901, 145.35525, "Nominatim: Belgrave railway station (Metro)"),
 "m_pbbel":     (-37.90768, 145.35657, "Nominatim: Belgrave (Narrow-gauge) — Puffing Billy"),
 "m_lakeside":  (-37.93040, 145.45965, "Nominatim: Lakeside railway station, Emerald (Puffing Billy)"),
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
