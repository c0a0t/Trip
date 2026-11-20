import osm
probes = {"ECQ promenade": (-33.8590,151.2137), "SOH car": (-33.85903,151.21414), "Hyde Park fountain": (-33.8712,151.2121), "Alfred St": (-33.86162,151.21134)}
for name,(la,lo) in probes.items():
    print("==", name)
    for e in osm.overpass(f'way["highway"](around:25,{la},{lo});out tags center;'):
        t = e.get("tags", {}); c = e.get("center", {})
        print(" ", e["id"], round(c.get("lat",0),5), round(c.get("lon",0),5), t.get("highway"), repr(t.get("name")), "layer=",t.get("layer"), "bridge=",t.get("bridge"), "tunnel=",t.get("tunnel"), "level=",t.get("level"), "indoor=",t.get("indoor"), "access=",t.get("access"), "motor=",t.get("motor_vehicle"))
print("== coastline count")
els = osm.overpass('way["natural"="coastline"](-33.866,151.195,-33.835,151.250);out ids;')
print(len(els))
els = osm.overpass('(way["natural"="water"](-33.866,151.195,-33.835,151.250);relation["natural"="water"](-33.866,151.195,-33.835,151.250););out tags;')
for e in els[:15]: print(" ", e["type"], e["id"], e.get("tags",{}).get("name"), e.get("tags",{}).get("water"))
