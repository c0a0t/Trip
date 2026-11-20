import json, sys, osm, pathlib
GEO = {k: tuple(v["ll"]) for k, v in json.loads(pathlib.Path("geo.json").read_text(encoding="utf-8")).items()}
def near(profile, p, n=4):
    url = f"https://routing.openstreetmap.de/routed-{profile}/nearest/v1/driving/{p[1]:.6f},{p[0]:.6f}?number={n}"
    osm._throttle("osrm", 1.1)
    r = osm.get(url)
    return [(w["name"], round(w["distance"]), [round(w["location"][1],5), round(w["location"][0],5)]) for w in r["waypoints"]]
tests = [("foot","dawes"),("foot","cq"),("foot","hydepark"),("foot","fish"),("foot","soh"),("foot","barangaroo"),("car","soh"),("car","cq"),("foot","milsonpark")]
for prof,k in tests: print(prof, k, GEO[k], near(prof, GEO[k]))
for p in [(-33.8580,151.2095),(-33.8604,151.2112),(-33.8598,151.2128),(-33.8714,151.2124),(-33.8590,151.2141),(-33.8617,151.2100),(-33.8565,151.2093)]:
    print("foot", p, near("foot", p)); print("car ", p, near("car", p, 2))
