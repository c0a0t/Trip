"""把要上线的网页文件复制到 site/，用于拖到 Netlify Drop（app.netlify.com/drop）。
用法：python build/make_site.py
只覆盖 site/ 里的这几个文件，不删除任何东西。"""
import json, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FILES = ["index.html", "app.js", "app.css", "data.js", "cairns.js", "geo.json", "routes.json", "tiletest.html",
         "vendor/leaflet/leaflet.js", "vendor/leaflet/leaflet.css"]

SITE.mkdir(exist_ok=True)
for f in FILES:
    (SITE / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / f, SITE / f)
for f in ("geo.json", "routes.json"):          # 确认 JSON 完整
    json.loads((SITE / f).read_text(encoding="utf-8"))
extra = sorted(p.name for p in SITE.iterdir() if p.name not in FILES and p.name != "vendor")
total = sum((SITE / f).stat().st_size for f in FILES)
print(f"site/ 已更新：{len(FILES)} 个文件，共 {total / 1024:.0f} KB")
for f in FILES: print(f"  {f:12s} {(SITE / f).stat().st_size / 1024:6.1f} KB")
if extra: print("注意：site/ 里还有不属于网页的文件，拖上去前请手动删掉：", extra)
