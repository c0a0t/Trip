# 悉尼 11.24–11.29 行程地图

静态网页：`index.html` + `app.js` + `app.css` + `data.js`（悉尼行程数据，原样摘自 `../itinerary-source.html`）+ `cairns.js`（凯恩斯 11/29–12/2，按常见一日团补全，时间以团为准；住处待定）+ `geo.json`（核准坐标）+ `routes.json`（构建期算好的真实路线）。
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
