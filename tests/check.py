"""Playwright 检查：桌面 1400×860（Chromium），以及 iPhone 15 Pro / iPhone SE（WebKit）和华为 Mate 40（Chromium）三种手机。
用法：先起本地服务器（python -m http.server 8765），再运行  python tests/check.py [http://127.0.0.1:8765/]
截图写到 screenshots/。"""
import json, math, pathlib, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
OUT = pathlib.Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)
results = []

def save_shot(page, path):
    # Windows 上截图文件偶尔被别的进程（预览/杀毒扫描）短暂占用，open 会报 Errno 22：稍等重试几次
    import time
    data = page.screenshot()
    for i in range(5):
        try:
            pathlib.Path(path).write_bytes(data); return
        except OSError as e:
            err = e; time.sleep(0.5 * (i + 1))
    print(f"WARN 截图没写成（文件被占用）：{pathlib.Path(path).name} {err}")

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))

def wait_idle(page, ms=900):
    page.wait_for_timeout(ms)
    page.wait_for_function("() => [...document.querySelectorAll('.leaflet-tile')].every(t => t.complete)", timeout=20000)

def attach_console(page, bucket):
    page.on("console", lambda m: bucket.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: bucket.append(f"pageerror: {e}"))
    # Leaflet 缩放/平移时会主动取消还没下完的瓦片（net::ERR_ABORTED），这是正常行为，不算报错
    page.on("requestfailed", lambda r: None if (("tile.openstreetmap.org" in r.url or "arcgisonline.com" in r.url) and "ERR_ABORTED" in (r.failure or ""))
            else bucket.append(f"requestfailed: {r.url} {r.failure}"))

def tiles_ok(page):
    return page.evaluate("""() => { const t=[...document.querySelectorAll('.leaflet-tile')];
        return {n:t.length, loaded:t.filter(x=>x.classList.contains('leaflet-tile-loaded')).length,
                bad:t.filter(x=>x.complete && x.naturalWidth===0).length} }""")

def legs_state(page):
    return page.evaluate("""() => { const a=__app; return a.legLines.map(x=>({k:`${x.lg.mode}:${x.lg.from}>${x.lg.to}`,
        real: !!a.ROUTES[`${x.lg.mode}:${x.lg.from}>${x.lg.to}`], n:x.ll.length})) }""")

def marker_xy(page, p):
    """标记在页面上的坐标"""
    return page.evaluate("""p => { const m=__app.map, P_=__app.markers.find(x=>x.p===p); if(!P_) return null;
        const r=document.getElementById('map').getBoundingClientRect(); const ll=P_.m.getLatLng(); const pt=m.latLngToContainerPoint(ll);
        return {x:r.left+pt.x, y:r.top+pt.y} }""", p)

def sel_state(page):
    """当前选中状态：选中的地点、地图上高亮的路段、行程里标出的行、标记是否在地图可见范围内、是否出现了气泡（应为没有）"""
    return page.evaluate("""() => { const a=__app, m=a.map, sel=a.state.sel;
        const on=a.legLines.filter(o=>o.line.options.opacity>=.99&&a.legLines.some(q=>q.line.options.opacity<.5)).map(o=>`${o.lg.from}>${o.lg.to}`);
        let visible=null; if(sel){const p=m.latLngToContainerPoint(P[sel].ll),s=m.getSize(); visible=p.x>=0&&p.y>=0&&p.x<=s.x&&p.y<=s.y}
        return {sel, on, rows:[...document.querySelectorAll('#content .sel')].map(e=>e.innerText.split(String.fromCharCode(10))[0].slice(0,24)),
                stops:[...document.querySelectorAll('#content .stop.sel')].map(e=>e.dataset.p),
                visible, popup: !!document.querySelector('.leaflet-popup')} }""")

def china_checks(page, tag, want):
    # 国内备用：Leaflet 从本站加载（不依赖 unpkg），苹果手机给“苹果地图”、安卓/华为给“本机地图”
    r = page.evaluate("""() => ({ext:performance.getEntriesByType('resource').map(e=>e.name).filter(u=>/unpkg|jsdelivr|cdnjs/.test(u)),
        vendor:[...document.scripts].some(s=>/vendor\/leaflet\/leaflet\.js$/.test(s.src)) && !!window.L && window.L.version})""")
    check(f"[{tag}] Leaflet 从本站加载，不连外部 CDN", r["vendor"] == "1.9.4" and not r["ext"], str(r))
    alt = page.evaluate("__app.ALT")
    check(f"[{tag}] 替代地图类型 = {want or '无'}", alt == want, alt)
    for d in ("day2", "cns3"):
        page.evaluate(f"__app.go('{d}')"); wait_idle(page, 500)
        info = page.evaluate("""() => ({legNav:document.querySelectorAll('.leg a.nav').length,
            legAlt:[...document.querySelectorAll('.leg a.nav2')].map(a=>a.getAttribute('href')),
            stops:document.querySelectorAll('.stop').length,
            stopAlt:[...document.querySelectorAll('.stop a.nav2')].map(a=>a.getAttribute('href'))})""")
        hrefs = info["legAlt"] + info["stopAlt"]
        if not want:
            check(f"[{tag}] {d}: 桌面不显示替代地图按钮", not hrefs, str(len(hrefs)))
            continue
        pre = "https://maps.apple.com/?" if want == "apple" else "geo:"
        okfmt = all(h.startswith(pre) for h in hrefs)
        if want == "apple":
            okfmt = okfmt and all(("saddr=" in h and "daddr=" in h and "dirflg=" in h) for h in info["legAlt"])
        check(f"[{tag}] {d}: 替代地图按钮 路段 {len(info['legAlt'])}/{info['legNav']}、地点 {len(info['stopAlt'])}/{info['stops']}",
              len(info["legAlt"]) == info["legNav"] and len(info["stopAlt"]) == info["stops"] and okfmt, hrefs[0] if hrefs else "")

def common_checks(page, tag):
    # 每天：路线全部来自 routes.json、图例、导航链接、Google 分段链接
    days = page.evaluate("DAYS.map(d=>d.id)")
    for d in days:
        page.evaluate(f"__app.go('{d}')"); wait_idle(page, 700)
        st = legs_state(page)
        check(f"[{tag}] {d}: {len(st)} 段路线都用真实路线", st and all(x["real"] for x in st), ",".join(x["k"] for x in st if not x["real"]))
        info = page.evaluate("""() => ({legend:document.getElementById('legend').innerText,
            nav:[...document.querySelectorAll('.leg')].map(l=>!!l.querySelector('a.nav')),
            to:[...document.querySelectorAll('.leg')].map(l=>l.innerText.slice(0,10)),
            gm:[...document.querySelectorAll('.gmrow')].map(a=>a.href)})""")
        modes = page.evaluate(f"[...new Set(__app.legLines.map(x=>MODES[x.lg.mode].n))]")
        check(f"[{tag}] {d}: 图例含 {'/'.join(modes)}", all(m in info["legend"] for m in modes))
        wps = [len(h.split("waypoints=")[1].split("&")[0].split("%7C")) if "waypoints=" in h else 0 for h in info["gm"]]
        check(f"[{tag}] {d}: Google 分段 {len(info['gm'])} 段，中途点最多 {max(wps or [0])} 个", info["gm"] and max(wps or [0]) <= 3)
        n_nav = sum(info["nav"])
        want = page.evaluate(f"(()=>{{const d=DAYS.find(x=>x.id==='{d}');const v=d.items.filter(i=>i.leg&&(!(i.v||i.vv)||(i.v||i.vv)===__app.state.variant[d.id]));return v.filter(i=>GMODE[i.mode]&&!i.nonav&&!__app.NO_NAV.includes(i.to)).length}})()")
        check(f"[{tag}] {d}: 路段导航链接 {n_nav}/{len(info['nav'])}（应有 {want}）", n_nav == want and want >= len(info["nav"]) - 8)
    # 方案切换（动物园那天：自己去 / 跟团）
    page.evaluate("__app.go('day3')"); wait_idle(page)
    page.click(".seg button[data-v='A']"); wait_idle(page, 400)
    txt = page.inner_text("#content")
    check(f"[{tag}] 11/27 方案 B→A 切换", "按团的集合时间" in txt and "Circular Quay 码头上船" not in txt)
    page.click(".seg button[data-v='B']"); wait_idle(page, 400)

def desktop(pw):
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1400, "height": 860}, device_scale_factor=1)
    page = ctx.new_page(); logs = []; attach_console(page, logs)
    page.goto(URL); page.wait_for_function("window.__app"); wait_idle(page, 1500)
    t = tiles_ok(page)
    check("[桌面] 总览瓦片加载", t["loaded"] > 4 and t["bad"] == 0, str(t))
    ov = page.inner_text("#content")
    check("[桌面] 总览：预订清单 + 注意事项 + 来源", all(s in ov for s in ["出发前要订的", "需要提前知道的", "来源"]))
    check("[桌面] OSM 署名", "OpenStreetMap" in page.inner_text(".leaflet-control-attribution"))
    save_shot(page, OUT / "desktop-overview.png")
    # 日期标签
    page.click("nav.tabs .tab:nth-child(5)"); wait_idle(page, 1200)
    check("[桌面] 点日期标签切到 11/26", page.evaluate("__app.state.day") == "day2" and "11/26" in page.inner_text(".dayhead"))
    save_shot(page, OUT / "desktop-day2.png")
    # “在 Google 地图看真实路线”默认收起，点一下展开
    page.evaluate("__app.go('day2')"); wait_idle(page, 600)
    closed = page.evaluate("!document.querySelector('details.gm').open")
    page.click("details.gm summary"); page.wait_for_timeout(200)
    opened = page.evaluate("document.querySelector('details.gm').open") and page.locator(".gmrow").first.is_visible()
    check("[桌面] Google 路线列表默认收起，点开可见", closed and opened)
    # 步行时间按 4 km/h 和真实路线长度重算（鱼市场→Broadway 1434 m ≈ 22 分钟；Argyle 上坡 518 m ×1.25 ≈ 10 分钟）
    page.evaluate("__app.go('day1')"); wait_idle(page, 600)
    t1 = page.inner_text("#content")
    page.evaluate("__app.go('day2')"); wait_idle(page, 600)
    t2 = page.inner_text("#content")
    check("[桌面] 步行时间按 4 km/h 重算", "约 22 分钟 · 1.4 km" in t1 and "约 10 分钟 · 520 m · 上坡" in t2 and "约 12 分钟 · 850 m" not in t1)
    # 时间线点地点 → 地图平移过去并高亮，不弹气泡
    page.click(".stop[data-p='bstairs'] h3"); page.wait_for_timeout(1300)
    st = sel_state(page)
    check("[桌面] 时间线点地点：地图平移到该点并高亮去它的路段，无气泡", st["sel"] == "bstairs" and st["visible"] and st["on"] == ["obs>bstairs"] and not st["popup"], str(st))
    save_shot(page, OUT / "desktop-stop-selected.png")
    check("[桌面] 每个地点一行里有 Google 地图链接", page.locator(".stop[data-p='bstairs'] a.nav").first.get_attribute("href").startswith("https://www.google.com/maps/search/"))
    # 地图上点标记
    page.evaluate("__app.go('day2')"); wait_idle(page, 1200)
    xy = marker_xy(page, "obs")
    page.mouse.click(xy["x"], xy["y"]); page.wait_for_timeout(1300)
    st = sel_state(page)
    check("[桌面] 地图上点标记 → 选中、行程标出这一站，无气泡", st["sel"] == "obs" and st["stops"] == ["obs"] and not st["popup"], str(st))
    mb = page.locator("#map").bounding_box()
    page.mouse.click(mb["x"] + 18, mb["y"] + mb["height"] * 0.55); page.wait_for_timeout(500)  # 地图左边缘，当天没有路线经过
    st = sel_state(page)
    check("[桌面] 点地图空白处 → 取消高亮", st["sel"] is None and not st["rows"] and not st["on"], str(st))
    # 点路段（时间线）→ 显示交通方式
    page.evaluate("__app.go('day2')"); wait_idle(page, 1000)
    z0 = page.evaluate("__app.map.getZoom()")
    page.click(".leg:has-text('渡轮') .mode"); page.wait_for_timeout(1400)
    st = sel_state(page); z1 = page.evaluate("__app.map.getZoom()")
    check("[桌面] 时间线点路段 → 平移到该段（不放大）并高亮，无气泡", st["on"] == ["mpwharf>cq"] and z1 <= z0 + 1e-6 and not st["popup"], f"zoom {z0}->{z1} {st}")
    save_shot(page, OUT / "desktop-leg-selected.png")
    # 地图上点路段
    page.evaluate("__app.go('day2')"); wait_idle(page, 1200)
    mid = page.evaluate("""() => { const x=__app.legLines.find(o=>o.lg.mode==='train'); const m=__app.map;
        const ll=x.ll[Math.floor(x.ll.length/2)]; const pt=m.latLngToContainerPoint(ll); const r=document.getElementById('map').getBoundingClientRect();
        return {x:r.left+pt.x, y:r.top+pt.y} }""")
    page.mouse.click(mid["x"], mid["y"]); page.wait_for_timeout(700)
    st = sel_state(page)
    check("[桌面] 地图上点路段 → 高亮并在行程里标出这一段", st["on"] == ["stjames>cqstn"] and any("火车" in r for r in st["rows"]) and not st["popup"], str(st))
    # 大桥那段确实在桥东侧人行道（Cahill Walk）
    r = page.evaluate("__app.ROUTES['walk:bstairs>milsonpark']")
    check("[桌面] 26 号 Bridge Stairs→McDougall St 走海港大桥东侧人行道", "Cahill Walk" in r.get("names", []), ",".join(r.get("names", [])))
    # 缩放到全悉尼含蓝山和机场
    page.evaluate("__app.go('day4')"); wait_idle(page, 1500)
    b = page.evaluate("(()=>{const b=__app.map.getBounds();return [b.getWest(),b.getEast(),b.getSouth(),b.getNorth()]})()")
    check("[桌面] 11/28 视野包含蓝山 Scenic World 和 Echo Point", b[0] < 150.30 and b[1] > 151.2, str([round(v, 3) for v in b]))
    save_shot(page, OUT / "desktop-day4-bluemountains.png")
    calendar_checks(page, "桌面", lambda n: save_shot(page, OUT / f"desktop-{n}.png"))
    with page.expect_download() as dl:
        page.click("#icsbtn")
    d = dl.value; body = open(d.path(), encoding="utf-8").read()
    check("[桌面] 点“加到手机日历”下载 trip-calendar.ics", d.suggested_filename == "trip-calendar.ics" and body.count("BEGIN:VEVENT") == 20, d.suggested_filename)
    common_checks(page, "桌面")
    china_checks(page, "桌面", "")
    page.evaluate("__app.go(null)"); wait_idle(page, 800)
    errs = [l for l in logs if not l.startswith("warning")]
    check("[桌面] 控制台无报错", not errs, " | ".join(errs[:5]))
    br.close()

IOS_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
# 手机机型：iPhone 用 WebKit（Safari 内核）；华为 Mate 40 用 Chromium（华为浏览器基于 Chromium），屏幕 2376×1080 @3x → 360 CSS px 宽
PROFILES = {
    "iphone15pro": dict(label="iPhone 15 Pro", engine="webkit", viewport={"width": 393, "height": 659}, screen={"width": 393, "height": 852}, dpr=3, ua=IOS_UA),
    "iphonese":    dict(label="iPhone SE", engine="webkit", viewport={"width": 375, "height": 553}, screen={"width": 375, "height": 667}, dpr=2, ua=IOS_UA),
    "mate40":      dict(label="华为 Mate 40", engine="chromium", viewport={"width": 360, "height": 720}, screen={"width": 360, "height": 792}, dpr=3,
                        ua="Mozilla/5.0 (Linux; Android 10; OCE-AN10; HMSCore 6.13.0.302) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 HuaweiBrowser/15.0.4.312 Mobile Safari/537.36"),
}

# iOS Safari 支持原生触摸，Leaflet 1.9 在这种浏览器里只听 TouchEvent（L.Browser.touchNative=true）。
# Playwright 的 WebKit 不允许 new Touch()，所以构造一个带 touches/changedTouches 列表的触摸事件，结构和 Safari 发给 Leaflet 的一致。
TOUCH_JS = """([type, pts]) => {
  const tgt = window.__touchTgt = (type === 'touchstart' || !window.__touchTgt) ? document.elementFromPoint(pts[0][1], pts[0][2]) : window.__touchTgt;
  const list = pts.map(([id, x, y]) => ({identifier: id, target: tgt, clientX: x, clientY: y, pageX: x + scrollX, pageY: y + scrollY, screenX: x, screenY: y, radiusX: 10, radiusY: 10, force: .5}));
  const ev = new Event(type, {bubbles: true, cancelable: true, composed: true});
  const active = type === 'touchend' ? [] : list;
  for (const [k, v] of [['touches', active], ['targetTouches', active], ['changedTouches', list]]) Object.defineProperty(ev, k, {value: v});
  tgt.dispatchEvent(ev);
  return ev.defaultPrevented; }"""

class Fingers:
    """多指手势。Chromium 用 CDP 发真实触摸事件；WebKit 没有 CDP，改为在页面里派发触摸事件（见 TOUCH_JS）"""
    def __init__(self, page, cdp): self.page, self.cdp, self.last = page, cdp, []
    def _send(self, typ, pts):
        if self.cdp:
            self.cdp.send("Input.dispatchTouchEvent", {"type": typ, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)]})
        else:
            self.page.evaluate(TOUCH_JS, [typ.lower(), [[i, x, y] for i, (x, y) in enumerate(pts)]])
    def start(self, pts): self.last = pts; self._send("touchStart", pts)
    def move(self, pts): self.last = pts; self._send("touchMove", pts)
    def end(self): self._send("touchEnd", [] if self.cdp else self.last)

def calendar_checks(page, tag, shot):
    # 日历标签
    page.click("nav.tabs .tab:nth-child(2)"); wait_idle(page, 900)
    st = page.evaluate("""() => ({view:__app.state.view, day:__app.state.day, hash:location.hash,
        on:document.querySelector('#tabs .tab.on').innerText,
        cells:[...document.querySelectorAll('.cal .c.trip')].map(c=>c.innerText.replace(/\\s+/g,' ')),
        ag:[...document.querySelectorAll('.ag')].map(a=>[...a.querySelectorAll('li')].map(l=>l.innerText.replace(/\\s+/g,' '))),
        head:document.querySelector('.cal .mh').innerText})""")
    check(f"[{tag}] 日历标签：切过去、地址 #calendar", st["view"] == "cal" and st["day"] is None and st["hash"] == "#calendar" and st["on"] == "日历", str({k: st[k] for k in ("view", "hash", "on")}))
    cal_days = page.evaluate("[...document.querySelectorAll('.cal .c[data-iso]')].map(c=>c.dataset.iso)")
    check(f"[{tag}] 日历：2026 年 11–12 月，11/16–12/13 四周", "2026 年 11–12 月" in st["head"] and cal_days[:1] == ["2026-11-16"] and cal_days[-1:] == ["2026-12-13"] and len(cal_days) == 28, f"{st['head']} {cal_days[:1]}…{cal_days[-1:]} n={len(cal_days)}")
    want_cells = ["24 落地 夜景", "25 奥莱 始祖鸟", "26 歌剧院 大桥", "27 动物园", "28 蓝山 一日团", "29 皮划艇 Bondi", "30 退房 凯恩斯",
                  "12/1 大堡礁", "2 库兰达 缆车火车", "3 海钓", "4 休整", "5 退房 阿德莱德",
                  "6 市集 做饭", "7 奔富 酒庄", "8 退房 墨尔本", "9 大洋路 十二门徒", "10 蒸汽 小火车"]
    check(f"[{tag}] 11/24–12/10 每天一格有简称（17 格）", st["cells"] == want_cells, str(st["cells"]))
    ag = st["ag"]
    check(f"[{tag}] 每日简表：20 页（换城市那天出发 / 到达各一张），每条带时间", len(ag) == 20 and all(1 <= len(a) <= 5 for a in ag)
          and ag[0][0] == "12:00 抵达住处" and ag[1][0] == "10:00 DFO 奥特莱斯" and "16:15 出园坐船回" in ag[3] and "11:00 取行李去机场" in ag[6]
          and ag[7][0] == "按航班 抵达凯恩斯机场" and "约 11:00 浮潜 / 玻璃底船 / 午餐" in ag[8] and ag[9][0] == "约 08:30 缆车上山"
          and ag[12][-1] == "按航班 飞阿德莱德" and "17:30 在家做饭" in ag[14] and ag[19][0] == "09:00 坐火车去 Belgrave", str(ag))
    cities = page.evaluate("[...document.querySelectorAll('.agenda h3.city')].map(h=>h.innerText)")
    check(f"[{tag}] 简表按城市分组", cities == ["悉尼 · 11/24–11/30", "凯恩斯 · 11/30–12/5", "阿德莱德 · 12/5–12/8", "墨尔本 · 12/8–12/10"], str(cities))
    ov = page.evaluate("""() => { const bad=[...document.querySelectorAll('.cal .c, .ag')].filter(e=>e.scrollWidth>e.clientWidth+1).length;
        return {sw:document.documentElement.scrollWidth, vw:innerWidth, bad} }""")
    check(f"[{tag}] 日历不撑出横向滚动、格子文字不溢出", ov["sw"] <= ov["vw"] and ov["bad"] == 0, str(ov))
    shot("calendar")
    # “今天”标记
    page.evaluate("window.__TODAY='2026-11-21'; __app.go('cal')"); page.wait_for_timeout(200)
    s1 = page.inner_text(".cal .mh .status")
    page.evaluate("window.__TODAY='2026-11-26'; __app.go('cal')"); page.wait_for_timeout(200)
    s2 = page.evaluate("""() => ({s:document.querySelector('.cal .mh .status').innerText, cell:(document.querySelector('.cal .c.today')||{dataset:{}}).dataset.go,
        ag:(document.querySelector('.ag.today')||{dataset:{}}).dataset.day})""")
    check(f"[{tag}] 出发前显示倒计时、行程中标出今天", s1 == "还有 3 天出发" and s2 == {"s": "今天是第 3 天", "cell": "day2", "ag": "day2"}, f"{s1} | {s2}")
    shot("calendar-today")
    page.evaluate("window.__TODAY='2026-12-01'; __app.go('cal')"); page.wait_for_timeout(200)
    s3 = page.evaluate("""() => ({s:document.querySelector('.cal .mh .status').innerText, cell:(document.querySelector('.cal .c.today')||{dataset:{}}).dataset.go,
        ag:(document.querySelector('.ag.today')||{dataset:{}}).dataset.day})""")
    page.evaluate("window.__TODAY='2026-12-10'; __app.go('cal')"); page.wait_for_timeout(200)
    s5 = page.evaluate("[document.querySelector('.cal .mh .status').innerText, (document.querySelector('.cal .c.today')||{dataset:{}}).dataset.go]")
    page.evaluate("window.__TODAY='2026-12-11'; __app.go('cal')"); page.wait_for_timeout(200)
    s4 = page.inner_text(".cal .mh .status")
    check(f"[{tag}] 凯恩斯、墨尔本那几天也标今天、结束后显示已结束", s3 == {"s": "今天是第 8 天", "cell": "cns2", "ag": "cns2"} and s5 == ["今天是第 17 天", "mel3"] and s4 == "行程已结束", f"{s3} | {s5} | {s4}")
    page.evaluate("delete window.__TODAY; __app.go('cal')"); page.wait_for_timeout(200)
    # .ics
    ics = page.evaluate("__app.icsText()")
    CRLF = chr(13) + chr(10)
    lines = ics.split(CRLF)
    ev = ics.count("BEGIN:VEVENT")
    starts = [l.split(":")[1] for l in lines if l.startswith("DTSTART")]
    longest = max(len(l.encode("utf-8")) for l in lines)
    unfold = ics.replace(CRLF + " ", "")
    want_starts = [f"202611{d}" for d in range(24, 31)] + ["20261130"] + [f"202612{d:02d}" for d in range(1, 6)] + ["20261205", "20261206", "20261207", "20261208", "20261208", "20261209", "20261210"]
    check(f"[{tag}] .ics：20 个全天日程（11/24–12/10），折行合规", ev == 20 and starts == want_starts and longest <= 75
          and "SUMMARY:悉尼 · 动物园" in unfold and "SUMMARY:凯恩斯 · 大堡礁：Reef Magic 坐船去、直升机飞回" in unfold
          and "SUMMARY:墨尔本 · 普芬比利蒸汽小火车" in unfold and "X-WR-CALNAME:澳洲行程 11/24–12/10" in unfold and "DTEND;VALUE=DATE:20261211" in unfold
          and "#day3" in unfold and ics.endswith(CRLF), f"ev={ev} starts={starts} longest={longest}")
    # 凯恩斯格子 → 进凯恩斯那天，地图跳到凯恩斯；再回悉尼，地图跳回悉尼
    page.click(".cal .c.trip[data-go='cns2']"); wait_idle(page, 1500)
    cn = page.evaluate("""() => { const c=__app.map.getCenter(), b=__app.map.options.maxBounds;
        return {day:__app.state.day, lat:+c.lat.toFixed(3), lng:+c.lng.toFixed(3), kicker:document.querySelector('.dayhead .kicker').innerText,
                maxS:b?+b.getSouth().toFixed(2):null} }""")
    t = tiles_ok(page)
    page.evaluate("__app.go('day1')"); wait_idle(page, 1200)
    sy = page.evaluate("(()=>{const c=__app.map.getCenter(), b=__app.map.options.maxBounds;return {lat:+c.lat.toFixed(3), maxS:b?+b.getSouth().toFixed(2):null}})()")
    check(f"[{tag}] 点凯恩斯日期 → 地图跳到凯恩斯（瓦片正常），回悉尼再跳回", cn["day"] == "cns2" and -17.0 < cn["lat"] < -16.8 and "凯恩斯" in cn["kicker"] and cn["maxS"] == -17.35
          and t["loaded"] >= 4 and t["bad"] == 0 and -34.0 < sy["lat"] < -33.8 and sy["maxS"] == -34.25, f"{cn} tiles={t} | {sy}")
    shot("cairns-reef")
    page.evaluate("__app.go('cns3')"); wait_idle(page, 1500); shot("cairns-kuranda")
    # 阿德莱德、墨尔本：地图跳过去，大洋路一整天都在视野里
    page.evaluate("__app.go('adl3')"); wait_idle(page, 1500)
    ad = page.evaluate("(()=>{const c=__app.map.getCenter(), b=__app.map.options.maxBounds;return {lat:+c.lat.toFixed(3), maxS:b?+b.getSouth().toFixed(2):null, kicker:document.querySelector('.dayhead .kicker').innerText}})()")
    t_ad = tiles_ok(page); shot("adelaide-penfolds")
    page.evaluate("__app.go('mel2')"); wait_idle(page, 2000)
    me = page.evaluate("""(()=>{const m=__app.map,b=m.getBounds(),mb=m.options.maxBounds;
        const inb=k=>b.contains(P[k].ll);
        return {maxS:mb?+mb.getSouth().toFixed(2):null, minZ:m.getMinZoom(), all:['m_meet','m_arch','m_apollo','m_12a','m_lochard'].every(inb), kicker:document.querySelector('.dayhead .kicker').innerText}})()""")
    t_me = tiles_ok(page); shot("melbourne-gor")
    page.evaluate("__app.go('mel3')"); wait_idle(page, 1500); shot("melbourne-puffingbilly")
    check(f"[{tag}] 点阿德莱德 / 墨尔本日期 → 地图跳过去（瓦片正常），大洋路全程在视野里",
          -35.0 < ad["lat"] < -34.85 and ad["maxS"] == -35.15 and "阿德莱德" in ad["kicker"] and t_ad["bad"] == 0
          and me["maxS"] == -39.05 and me["minZ"] == 7 and me["all"] and "墨尔本" in me["kicker"] and t_me["bad"] == 0, f"{ad} {t_ad} | {me} {t_me}")
    page.evaluate("__app.go('cal')"); wait_idle(page, 500)
    # 点日历格子 / 简表卡片 → 去那天
    page.click(".cal .c.trip[data-go='day4']"); wait_idle(page, 700)
    a = page.evaluate("[__app.state.day, __app.state.view, location.hash]")
    page.evaluate("__app.go('cal')"); wait_idle(page, 500)
    page.click(".ag[data-day='kayak']"); wait_idle(page, 700)
    b = page.evaluate("[__app.state.day, __app.state.view]")
    check(f"[{tag}] 点日历格子/简表 → 进到那一天", a == ["day4", None, "#day4"] and b == ["kayak", None], f"{a} {b}")
    page.evaluate("__app.go('cal')"); wait_idle(page, 300)

def mobile(pw, key):
    pf = PROFILES[key]; tag = pf["label"]
    br = getattr(pw, pf["engine"]).launch()
    ctx = br.new_context(viewport=pf["viewport"], screen=pf["screen"], device_scale_factor=pf["dpr"], is_mobile=True, has_touch=True, user_agent=pf["ua"])
    page = ctx.new_page(); logs = []; attach_console(page, logs)
    fingers = Fingers(page, ctx.new_cdp_session(page) if pf["engine"] == "chromium" else None)
    VH = pf["viewport"]["height"]
    shot = lambda name: save_shot(page, OUT / f"{key}-{name}.png")
    page.goto(URL + "#day2"); page.wait_for_function("window.__app"); wait_idle(page, 1500)
    check(f"[{tag}] 浏览器内核", True, page.evaluate("navigator.userAgent")[:60] + f"… engine={pf['engine']}")
    t = tiles_ok(page)
    check(f"[{tag}] 瓦片加载", t["n"] >= 4 and t["loaded"] == t["n"] and t["bad"] == 0, str(t))
    shot("day2-top")
    # 吸顶：滚动后日期栏和地图都固定在顶部
    page.evaluate("window.scrollTo(0, 900)"); page.wait_for_timeout(500)
    g = page.evaluate("""() => { const t=document.getElementById('tabs').getBoundingClientRect(), m=document.getElementById('mapwrap').getBoundingClientRect();
        return {scrollY:scrollY, tabsTop:t.top, tabsBottom:t.bottom, mapTop:m.top, mapH:m.height} }""")
    check(f"[{tag}] 往下滚时间线：日期栏和地图固定在顶部", g["scrollY"] > 300 and abs(g["tabsTop"]) < 1 and abs(g["mapTop"] - g["tabsBottom"]) < 2, str(g))
    shot("day2-scrolled")
    page.evaluate("window.scrollTo(0, 0)"); page.wait_for_timeout(300)
    box = page.locator("#map").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    # 单指拖动：地图平移，页面不滚动
    c0 = page.evaluate("__app.map.getCenter()"); y0 = page.evaluate("scrollY")
    fingers.start([(cx, cy)])
    for i in range(1, 11): fingers.move([(cx - 8 * i, cy + 6 * i)]); page.wait_for_timeout(16)
    fingers.end(); page.wait_for_timeout(600)
    c1 = page.evaluate("__app.map.getCenter()"); y1 = page.evaluate("scrollY")
    check(f"[{tag}] 单指拖动只移动地图", (abs(c1["lat"] - c0["lat"]) + abs(c1["lng"] - c0["lng"])) > 1e-4 and y1 == y0, f"scroll {y0}->{y1}")
    # 双指缩放：地图放大，网页本身不缩放
    z0 = page.evaluate("__app.map.getZoom()")
    fingers.start([(cx - 30, cy), (cx + 30, cy)])
    for i in range(1, 13): fingers.move([(cx - 30 - 9 * i, cy), (cx + 30 + 9 * i, cy)]); page.wait_for_timeout(16)
    fingers.end(); page.wait_for_timeout(900)
    z1 = page.evaluate("__app.map.getZoom()"); vs = page.evaluate("visualViewport.scale")
    check(f"[{tag}] 双指缩放只缩放地图", z1 > z0 + 0.5 and abs(vs - 1) < 1e-6, f"zoom {z0}->{z1}, page scale {vs}")
    # 靠得近的标记：点在两个标记之间偏向某一个，应选中最近的那个
    page.evaluate("__app.go('day2')"); wait_idle(page, 1200)
    for tgt, other, frac in (("stmary", "hpb", 0.62), ("hpb", "stmary", 0.38)):
        # 从地图选中地点后页面会平滑滚到时间线对应条目，所以每次都重新定位、等滚动停下再算坐标
        page.evaluate("__app.state.sel=null; __app.map.setView([-33.8705,151.2128],15,{animate:false})")
        page.wait_for_timeout(900)
        a, b = marker_xy(page, "hpb"), marker_xy(page, "stmary")
        d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
        tx, ty = a["x"] + (b["x"] - a["x"]) * frac, a["y"] + (b["y"] - a["y"]) * frac
        page.touchscreen.tap(tx, ty); page.wait_for_timeout(1300)
        check(f"[{tag}] 两个标记相距 {d:.0f}px，点偏向 {tgt} 的位置 → 选中 {tgt}", page.evaluate("__app.state.sel") == tgt, page.evaluate("__app.state.sel"))
    # 从行程选中地图边缘外的点：地图平移过去，点在可见范围内，不出气泡
    page.evaluate("__app.map.setView([-33.8705,151.2128],15,{animate:false})"); page.wait_for_timeout(400)
    for p in ("mpwharf", "soh", "home", "milsonpark"):
        page.evaluate(f"__app.selectStop('day2','{p}',false)"); page.wait_for_timeout(1000)
        st = sel_state(page)
        check(f"[{tag}] 选中 {p} → 平移到可见范围，无气泡", st["sel"] == p and st["visible"] and not st["popup"], str(st))
    shot("selected-edge")
    # 时间线点地点（手机）：只平移不缩放；高亮这个点和去它的路段；之后能自由拖走地图
    page.evaluate("__app.go('day2')"); wait_idle(page, 1200)
    page.evaluate("__app.map.setZoom(14,{animate:false})"); page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, 700)"); page.wait_for_timeout(300)
    z0 = page.evaluate("__app.map.getZoom()")
    page.locator(".stop[data-p='westfield']").tap(); page.wait_for_timeout(1400)
    z1 = page.evaluate("__app.map.getZoom()")
    st = sel_state(page)
    check(f"[{tag}] 时间线点地点 → 平移过去、缩放不变、无气泡", st["sel"] == "westfield" and st["visible"] and not st["popup"] and abs(z1 - z0) < 1e-6,
          f"zoom {z0}->{z1} {st}")
    hl = page.evaluate("""() => __app.legLines.map(o => ({k:`${o.lg.from}>${o.lg.to}`, op:o.line.options.opacity}))""")
    on = [x["k"] for x in hl if x["op"] >= 0.99]; off = [x for x in hl if x["op"] < 0.5]
    check(f"[{tag}] 高亮去这个地点的路段（其余变淡）", on == ["hydepark>westfield"] and len(off) == len(hl) - 1, f"高亮 {on}")
    sel_ok = page.evaluate("document.querySelector('.leg.sel') && document.querySelector('.leg.sel').innerText.includes('步行')")
    check(f"[{tag}] 时间线里对应路段同时标出", bool(sel_ok))
    shot("stop-selected")
    # 选中后拖走地图，不应被拉回到选中的地点
    box = page.locator("#map").bounding_box(); cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.7
    p0 = page.evaluate("(()=>{const p=__app.map.latLngToContainerPoint(P.westfield.ll);return [p.x,p.y]})()")
    fingers.start([(cx, cy)])
    for i in range(1, 13): fingers.move([(cx - 12 * i, cy - 4 * i)]); page.wait_for_timeout(16)
    fingers.end(); page.wait_for_timeout(1200)
    p1 = page.evaluate("(()=>{const p=__app.map.latLngToContainerPoint(P.westfield.ll);return [p.x,p.y]})()")
    check(f"[{tag}] 选中后可以自由拖动地图（不会弹回）", p1[0] < p0[0] - 100, f"标记 x {p0[0]:.0f} -> {p1[0]:.0f}")
    # 地图和行程之间的拖动条
    page.evaluate("window.scrollTo(0, 0)"); page.wait_for_timeout(300)
    def handle_y(): b = page.locator("#resizer").bounding_box(); return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    h0 = page.evaluate("document.getElementById('mapwrap').offsetHeight"); z0 = page.evaluate("__app.map.getZoom()")
    hx, hy = handle_y(); fingers.start([(hx, hy)])
    for i in range(1, 11): fingers.move([(hx, hy + 18 * i)]); page.wait_for_timeout(16)
    fingers.end(); page.wait_for_timeout(500)
    h1 = page.evaluate("document.getElementById('mapwrap').offsetHeight"); y1 = page.evaluate("scrollY")
    hb = page.locator("#resizer").bounding_box()
    check(f"[{tag}] 往下拖拖动条 → 地图变高、页面不滚动、拖动条仍在屏幕内", h1 > h0 + 100 and y1 == 0 and hb["y"] + hb["height"] <= VH,
          f"{h0}px -> {h1}px, scrollY {y1}, 拖动条底边 {hb['y'] + hb['height']:.0f}/{VH}")
    wait_idle(page, 600); shot("expanded")
    hx, hy = handle_y(); fingers.start([(hx, hy)])
    for i in range(1, 11): fingers.move([(hx, hy - 26 * i)]); page.wait_for_timeout(16)
    fingers.end(); page.wait_for_timeout(500)
    h2 = page.evaluate("document.getElementById('mapwrap').offsetHeight")
    check(f"[{tag}] 往上拖拖动条 → 地图变矮（下面行程变多）", h2 < h1 - 200 and h2 >= 160, f"{h1}px -> {h2}px")
    shot("collapsed")
    page.reload(); page.wait_for_function("window.__app"); page.wait_for_timeout(1200)
    h3 = page.evaluate("document.getElementById('mapwrap').offsetHeight")
    check(f"[{tag}] 刷新后记住拖好的高度", abs(h3 - h2) < 4, f"{h2}px / 刷新后 {h3}px")
    hx, hy = handle_y(); page.touchscreen.tap(hx, hy); page.wait_for_timeout(600)
    h4 = page.evaluate("document.getElementById('mapwrap').offsetHeight")
    check(f"[{tag}] 轻点拖动条 → 切到大半屏", h4 > VH * 0.66, f"{h3}px -> {h4}px")
    hx, hy = handle_y(); page.touchscreen.tap(hx, hy); page.wait_for_timeout(600)
    h5 = page.evaluate("document.getElementById('mapwrap').offsetHeight")
    check(f"[{tag}] 再轻点 → 回到默认高度", abs(h5 - VH * 0.46) < 6, f"{h4}px -> {h5}px")
    # 地图上点路段
    page.evaluate("__app.go('day3')"); wait_idle(page, 1300)
    mid = page.evaluate("""() => { const x=__app.legLines.find(o=>o.lg.mode==='ferry'); const m=__app.map;
        const ll=x.ll[Math.floor(x.ll.length*0.4)]; const pt=m.latLngToContainerPoint(ll); const r=document.getElementById('map').getBoundingClientRect();
        return {x:r.left+pt.x, y:r.top+pt.y} }""")
    page.touchscreen.tap(mid["x"], mid["y"]); page.wait_for_timeout(900)
    st = sel_state(page)
    check(f"[{tag}] 点地图上的路段 → 高亮并在行程里标出，无气泡", st["on"] == ["cq>zoowharf"] and any("渡轮" in r for r in st["rows"]) and not st["popup"], str(st))
    shot("day3-ferry")
    calendar_checks(page, tag, shot)
    common_checks(page, tag)
    china_checks(page, tag, "apple" if pf["engine"] == "webkit" else "geo")
    page.evaluate("__app.go(null)"); wait_idle(page, 1000)
    shot("overview")
    errs = [l for l in logs if not l.startswith("warning")]
    check(f"[{tag}] 控制台无报错", not errs, " | ".join(errs[:5]))
    br.close()

def basemap_checks(pw):
    # 国内网络：OpenStreetMap 瓦片打不开 → 自动换 Esri；?tiles=esri 直接用 Esri；测试页能打开
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1000, "height": 760})
    page = ctx.new_page()
    page.route("**/tile.openstreetmap.org/**", lambda r: r.abort())
    page.goto(URL + "#day2"); page.wait_for_function("window.__app")
    page.wait_for_timeout(500)
    k0 = page.evaluate("__app.baseKey")
    page.wait_for_function("__app.baseKey==='esri'", timeout=15000); wait_idle(page, 1500)
    t = tiles_ok(page)
    src = page.evaluate("[...document.querySelectorAll('.leaflet-tile')].map(x=>x.src).filter(u=>u.includes('arcgisonline')).length")
    attr = page.inner_text(".leaflet-control-attribution")
    check("[底图] OSM 被墙时自动换成 Esri", src > 4 and t["loaded"] == t["n"] and t["bad"] == 0 and "Esri" in attr, f"{k0} → esri, {t}, {attr[:40]}")
    save_shot(page, OUT / "desktop-basemap-esri.png")
    page.reload(); page.wait_for_function("window.__app"); page.wait_for_timeout(300)
    check("[底图] 换过一次后记在本机，下次直接用 Esri", page.evaluate("__app.baseKey") == "esri")
    ctx.close()
    ctx = br.new_context(viewport={"width": 1000, "height": 760}); page = ctx.new_page()
    page.goto(URL + "?tiles=esri#cns3"); page.wait_for_function("window.__app"); wait_idle(page, 1500)
    t = tiles_ok(page)
    check("[底图] ?tiles=esri 凯恩斯瓦片加载", page.evaluate("__app.baseKey") == "esri" and t["n"] >= 4 and t["loaded"] == t["n"] and t["bad"] == 0, str(t))
    page.goto(URL + "tiletest.html"); page.wait_for_function("document.getElementById('sum').textContent.startsWith('结果')", timeout=25000)
    check("[底图] 测试页三种底图都能加载（本机网络）", page.inner_text("#sum").count("能用") == 3 and "不能用" not in page.inner_text("#sum"), page.inner_text("#sum"))
    br.close()

with sync_playwright() as pw:
    desktop(pw)
    basemap_checks(pw)
    for k in PROFILES: mobile(pw, k)
fails = [r for r in results if not r[1]]
print(f"\n{len(results) - len(fails)}/{len(results)} 通过")
sys.exit(1 if fails else 0)
