import osm, json, pathlib
G = {k: tuple(v["ll"]) for k, v in json.loads(pathlib.Path("geo.json").read_text(encoding="utf-8")).items()}
for p in [(-33.85956,151.21303),(-33.86013,151.21308),(-33.85906,151.21326),(-33.85842,151.21355)]:
    osm._throttle("osrm",1.1)
    r = osm.get(f"https://routing.openstreetmap.de/routed-foot/nearest/v1/driving/{p[1]},{p[0]}?number=3")
    print(p, [(w["name"], round(w["distance"]), [round(w["location"][1],5), round(w["location"][0],5)]) for w in r["waypoints"]])
for via in [[(-33.85956,151.21303)], [(-33.86013,151.21308),(-33.85906,151.21326)]]:
    r = osm.osrm("foot", [G["cq"], *via, G["soh"]], radiuses=";".join(["unlimited"]+["20"]*len(via)+["unlimited"]))
    names=[s.get("name") for lg in r["legs"] for s in lg["steps"] if s.get("name")]
    print(via, round(r["distance"]), names)
