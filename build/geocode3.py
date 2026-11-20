import osm
for e in osm.overpass('(nwr["name"~"Quadrangle"](-33.892,151.183,-33.882,151.195);nwr["natural"="beach"](-33.900,151.265,-33.885,151.285););out center tags;'):
    c = e.get("center", e); print(e["type"], e["id"], round(c["lat"],5), round(c["lon"],5), e["tags"].get("name"), e["tags"].get("building") or e["tags"].get("natural"))
