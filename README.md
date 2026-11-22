# 澳洲 11.24–12.10 行程地图（悉尼 → 凯恩斯 → 阿德莱德 → 墨尔本）

静态网页：`index.html` + `app.js` + `app.css` + `data.js`（悉尼 11/24–11/30，最初摘自 `../itinerary-source.html`，2026-11-22 按新安排调整）+ `cairns.js`（凯恩斯 11/30–12/5）+ `adelaide.js`（阿德莱德 12/5–12/8）+ `melbourne.js`（墨尔本 12/8–12/10）+ `geo.json`（核准坐标）+ `routes.json`（构建期算好的真实路线）。
底图是 Leaflet + OpenStreetMap 标准瓦片；页面运行时不调用任何路线服务。

## 重新构建（只在改了地点或路段时需要）

```powershell
cd sydney-trip-map
C:\ZMySoftware\ANACONDA\python.exe -m venv .venv
.venv\Scripts\python.exe -m pip install playwright pillow
.venv\Scripts\python.exe -m playwright install chromium
.venv\Scripts\python.exe build\places.py      # 坐标 -> geo.json（来源写在每条的 src 里）
.venv\Scripts\python.exe build\routes.py      # 路线 -> routes.json（可只重算某段：build\routes.py "walk:bstairs>milsonpark"）
```

- 步行：FOSSGIS OSRM foot；打车/团车/238 路公交：OSRM car。歌剧院、环形码头、Dawes Point、海德公园这几个点上下有高架/桥面/站台，用 `ANCHOR` 指定地面路由点。
- 火车（City Circle）、L3 轻轨、渡轮：OSM 线路几何上做最短路。渡轮用 OSM 瓦片像素做“全程在水面上”校验（海港大桥桥面、海港隧道两处豁免），失败会退回 `FERRY_MANUAL` 手工水道。
- 动物园园内步行是示意线。

## 测试

```powershell
.venv\Scripts\python.exe -m http.server 8765
.venv\Scripts\python.exe tests\check.py http://127.0.0.1:8765/
```

桌面 1400×860 和手机 390×844（触屏）两套检查，截图在 `screenshots/`。
