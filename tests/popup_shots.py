"""弹窗前后对比截图：Mate 40 尺寸，地点弹窗 + 路段弹窗。用法：python tests/popup_shots.py <url> <前缀>"""
import sys
from playwright.sync_api import sync_playwright
url, tag = sys.argv[1], sys.argv[2]
with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 360, "height": 720}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = ctx.new_page(); page.goto(url + "#day2"); page.wait_for_function("window.__app"); page.wait_for_timeout(2500)
    page.evaluate("__app.map.setView([-33.8600,151.2100],15,{animate:false})"); page.wait_for_timeout(800)
    page.evaluate("__app.selectStop('day2','soh',false)"); page.wait_for_timeout(1800)
    page.locator("#mapwrap").screenshot(path=f"screenshots/{tag}-popup-stop.png")
    page.evaluate("__app.map.closePopup()")
    page.locator(".leg:has-text('渡轮') .mode").first.tap(); page.wait_for_timeout(1500)
    page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(400)
    page.locator("#mapwrap").screenshot(path=f"screenshots/{tag}-popup-leg.png")
    br.close()
