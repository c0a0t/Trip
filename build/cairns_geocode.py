"""凯恩斯地点：Nominatim 查询（≤1 次/秒，带 UA），打印候选，人工挑选后写进 places.py 的 FINAL。"""
import json, pathlib
import osm

Q = {
 "c_airport":   [dict(q="Cairns Airport Domestic Terminal"), dict(q="Cairns Airport")],
 "c_home":      [dict(q="City Place, Cairns City"), dict(q="Cairns City Place")],
 "c_lagoon":    [dict(q="Cairns Esplanade Lagoon"), dict(q="Esplanade Lagoon, Cairns")],
 "c_nightmkt":  [dict(q="Cairns Night Markets")],
 "c_reeffleet": [dict(q="Reef Fleet Terminal, Cairns"), dict(q="Reef Fleet Terminal")],
 "c_reef":      [dict(q="Moore Reef, Queensland"), dict(q="Moore Reef")],
 "c_cnsstn":    [dict(q="Cairns railway station"), dict(q="Cairns Station, Bunda Street")],
 "c_freshwater":[dict(q="Freshwater railway station, Queensland"), dict(q="Freshwater Station, Cairns")],
 "c_barron":    [dict(q="Barron Falls railway station"), dict(q="Barron Falls Station, Kuranda")],
 "c_kuranda":   [dict(q="Kuranda railway station"), dict(q="Kuranda Station")],
 "c_kvillage":  [dict(q="Kuranda Heritage Markets"), dict(q="Kuranda Original Rainforest Markets")],
 "c_skyk":      [dict(q="Skyrail Kuranda Terminal"), dict(q="Skyrail Rainforest Cableway Kuranda")],
 "c_skys":      [dict(q="Skyrail Smithfield Terminal"), dict(q="Skyrail Rainforest Cableway Caravonica")],
}
out = {}
for k, qs in Q.items():
    out[k] = []
    for params in qs:
        try:
            res = osm.nominatim(**params)
        except Exception as e:
            print(k, "ERR", e); continue
        for r in res:
            out[k].append({"q": params["q"], "ll": [round(float(r["lat"]), 5), round(float(r["lon"]), 5)],
                           "cat": f'{r.get("category")}/{r.get("type")}', "name": r.get("display_name", "")[:110]})
        if res: break
    print(f"\n{k}:")
    for c in out[k]: print(f'   {c["ll"]}  {c["cat"]:28s} {c["name"]}')
(pathlib.Path(__file__).parent / "cairns-geocode-raw.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
