import urllib.request, xml.etree.ElementTree as ET, sys
from osm import UA
bbox = sys.argv[1]
x = urllib.request.urlopen(urllib.request.Request(f"https://api.openstreetmap.org/api/0.6/map?bbox={bbox}", headers={"User-Agent": UA}), timeout=60).read()
root = ET.fromstring(x)
nodes = {n.get("id"): (float(n.get("lat")), float(n.get("lon"))) for n in root.iter("node")}
for w in root.iter("way"):
    t = {tg.get("k"): tg.get("v") for tg in w.iter("tag")}
    if "highway" not in t: continue
    pts = [nodes.get(nd.get("ref")) for nd in w.iter("nd")]
    pts = [p for p in pts if p]
    lo = min(p[1] for p in pts); hi = max(p[1] for p in pts); la = sum(p[0] for p in pts)/len(pts)
    print(w.get("id"), t.get("highway"), repr(t.get("name")), "layer=",t.get("layer"), "bridge=",t.get("bridge"), "covered=",t.get("covered"), f"lat~{la:.5f} lng {lo:.5f}-{hi:.5f}", len(pts))
