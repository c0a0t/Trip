import osm, json, pathlib, urllib.parse
G = {k: tuple(v["ll"]) for k, v in json.loads(pathlib.Path("geo.json").read_text(encoding="utf-8")).items()}
def tr(label, prof, pts, rad=None):
    extra = {}
    if rad: extra["radiuses"] = ";".join(str(r) if r else "unlimited" for r in rad)
    try:
        r = osm.osrm(prof, pts, **extra)
    except Exception as e:
        print(label, "FAIL", e); return
    names = []
    for lg in r["legs"]:
        for s in lg["steps"]:
            n = s.get("name") or ""
            if n and (not names or names[-1] != n): names.append(n)
    print(f"{label:34s} {r['distance']:7.0f} m  {' / '.join(names[:9])}")
tr("cq>soh no via", "foot", [G["cq"], G["soh"]])
tr("cq>soh via ECQ -33.8585,151.2133 r8", "foot", [G["cq"], (-33.8585,151.2133), G["soh"]], [None, 8, None])
tr("cq>soh via -33.8592,151.2134 r8", "foot", [G["cq"], (-33.8592,151.2134), G["soh"]], [None, 8, None])
tr("dawes>cq anchor", "foot", [(-33.85602,151.20934), G["cq"]], [15, None])
tr("dawes>cq anchor via cove", "foot", [(-33.85602,151.20934), (-33.8580,151.2095), G["cq"]], [15, 10, None])
tr("barangaroo>dawes anchor", "foot", [G["barangaroo"], (-33.8564,151.2042), (-33.8556,151.2064), (-33.85602,151.20934)], [None, None, None, 15])
tr("stmary>hydepark", "foot", [G["stmary"], (-33.8714,151.2124)], [None, 12])
tr("hydepark>westfield", "foot", [(-33.8714,151.2124), G["westfield"]], [12, None])
tr("hpb>stmary", "foot", [G["hpb"], G["stmary"]])
tr("car home>soh anchor", "car", [G["home"], (-33.85903,151.21414)], [None, 10])
tr("car soh>broadway anchor", "car", [(-33.85903,151.21414), G["broadway"]], [10, None])
tr("car home>cq Alfred", "car", [G["home"], (-33.86162,151.21134)], [None, 10])
tr("car cq Alfred>home", "car", [(-33.86162,151.21134), G["home"]], [10, None])
tr("foot home>fish", "foot", [G["home"], G["fish"]])
tr("foot fish>broadway", "foot", [G["fish"], G["broadway"]])
tr("foot home>dh no via", "foot", [G["home"], G["dh"]])
tr("foot rbg>hpb no via", "foot", [G["rbg"], G["hpb"]])
