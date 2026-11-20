import osm
def show(q, title):
    print("==", title)
    for e in osm.overpass(q + "out tags center;"):
        t = e.get("tags", {}); c = e.get("center", {})
        print(" ", e["id"], round(c.get("lat",0),5), round(c.get("lon",0),5), t.get("highway"), repr(t.get("name")), "layer=", t.get("layer"), "bridge=", t.get("bridge"), "level=", t.get("level"), "foot=", t.get("foot"), t.get("footway",""), t.get("sidewalk",""))
show('way["highway"](around:45,-33.8553,151.2092);', "Dawes Point")
show('way["highway"]["highway"!~"^(motorway|motorway_link|trunk|trunk_link|primary|service)$"](-33.8545,151.2080,-33.8505,151.2120);', "Harbour Bridge deck walkways")
