"""新加的地点（悉尼购物/皮划艇、凯恩斯新安排、阿德莱德、墨尔本）：Nominatim 查询（≤1 次/秒，带 UA），
打印候选，人工挑选后写进 places.py 的 FINAL。原始结果存 more-geocode-raw.json（不提交）。"""
import json, pathlib, sys
import osm

Q = {
 # 悉尼
 "s_dfo":      ["DFO Homebush", "DFO Homebush Underwood Road"],
 "s_mill":     ["The Mill, Bourke Road, Alexandria", "41 Bourke Road, Alexandria"],
 "s_lavender": ["Railway Avenue, Lavender Bay", "Lavender Bay"],
 "s_bronte":   ["Bronte Beach", "Bronte Beach, Sydney"],
 # 凯恩斯
 "c_rainf":    ["Rainforestation Nature Park", "Rainforestation, Kennedy Highway, Kuranda"],
 "c_marina":   ["Marlin Marina, Cairns", "Marlin Jetty, Cairns"],
 "c_rustys":   ["Rusty's Markets, Cairns", "Rusty's Markets"],
 "c_botanic":  ["Cairns Botanic Gardens", "Flecker Botanic Gardens"],
 "c_heli":     ["Nautilus Aviation, Cairns", "Nautilus Aviation"],
 # 阿德莱德
 "a_airport":  ["Adelaide Airport Terminal 1", "Adelaide Airport"],
 "a_home":     ["Victoria Square, Adelaide", "Victoria Square Tarntanyangga"],
 "a_central":  ["Adelaide Central Market", "Central Market, Gouger Street, Adelaide"],
 "a_farmers":  ["Adelaide Showground Farmers Market", "Adelaide Showground, Wayville"],
 "a_rundle":   ["Rundle Mall, Adelaide", "Rundle Mall"],
 "a_gallery":  ["Art Gallery of South Australia", "South Australian Museum"],
 "a_botanic":  ["Adelaide Botanic Garden", "Botanic Garden, Adelaide"],
 "a_elder":    ["Elder Park, Adelaide", "Elder Park"],
 "a_penfolds": ["Penfolds Magill Estate", "78 Penfold Road, Magill"],
 # 墨尔本
 "m_airport":  ["Melbourne Airport Terminal 1", "Melbourne Airport"],
 "m_home":     ["Melbourne Town Hall", "Bourke Street Mall, Melbourne"],
 "m_meet":     ["Federation Square, Melbourne", "Federation Square"],
 "m_flinders": ["Flinders Street railway station", "Flinders Street Station"],
 "m_arch":     ["Great Ocean Road Memorial Arch", "Memorial Arch, Eastern View"],
 "m_apollo":   ["Apollo Bay, Victoria", "Apollo Bay"],
 "m_12a":      ["Twelve Apostles, Port Campbell", "The Twelve Apostles"],
 "m_lochard":  ["Loch Ard Gorge", "Loch Ard Gorge, Port Campbell"],
 "m_belgrave": ["Belgrave railway station", "Belgrave Station, Victoria"],
 "m_pbbel":    ["Puffing Billy Belgrave Station", "Puffing Billy Railway Belgrave"],
 "m_lakeside": ["Lakeside railway station, Emerald", "Emerald Lake Park, Emerald"],
}
only = sys.argv[1:]
raw_f = pathlib.Path(__file__).parent / "more-geocode-raw.json"
out = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else {}
for k, qs in Q.items():
    if only and k not in only: continue
    out[k] = []
    for q in qs:
        try:
            res = osm.nominatim(q=q)
        except Exception as e:
            print(k, "ERR", e); continue
        for r in res:
            out[k].append({"q": q, "ll": [round(float(r["lat"]), 5), round(float(r["lon"]), 5)],
                           "cat": f'{r.get("category")}/{r.get("type")}', "name": r.get("display_name", "")[:110]})
    print(f"\n{k}:")
    for c in out[k][:6]: print(f'   {c["ll"]}  {c["cat"]:26s} {c["q"][:22]:22s} | {c["name"]}')
raw_f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
