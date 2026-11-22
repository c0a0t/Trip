/* 阿德莱德 12/5–12/8。用户的安排：
     12/5 从凯恩斯飞到 / 12/6（周日）Sunday market 买菜，下午市区转转，晚上在家做饭 / 12/7 奔富酒庄 / 12/8 飞墨尔本
   中央市场周日、周一不开，所以周日买菜去 Wayville 的 Adelaide Farmers' Market；奔富去离市区近的 Magill Estate。
   住处还没定，“家”先放在市中心 Victoria Square。坐标在 geo.json（build/places.py），路线在 routes.json（build/routes.py）。 */
Object.assign(P,{
 a_airport:{n:"阿德莱德机场",ll:[-34.93894,138.5375],q:"Adelaide Airport Terminal"},
 a_home:{n:"阿德莱德住处（待定 · 先放市中心）",ll:[-34.92895,138.59992],q:"Victoria Square, Adelaide SA",home:1},
 a_central:{n:"中央市场 Central Market",ll:[-34.93009,138.59805],q:"Adelaide Central Market"},
 a_farmers:{n:"Adelaide Farmers' Market（Wayville 展览馆）",ll:[-34.94596,138.58653],q:"Adelaide Farmers Market, Adelaide Showground, Wayville SA"},
 a_rundle:{n:"Rundle Mall 步行街",ll:[-34.92284,138.6026],q:"Rundle Mall, Adelaide"},
 a_gallery:{n:"North Terrace：南澳美术馆 / 博物馆",ll:[-34.92063,138.60397],q:"Art Gallery of South Australia"},
 a_botanic:{n:"阿德莱德植物园",ll:[-34.91823,138.61146],q:"Adelaide Botanic Garden"},
 a_river:{n:"托伦斯河边（Festival Centre 一带）",ll:[-34.91958,138.59779],q:"Adelaide Festival Centre"},
 a_penfolds:{n:"奔富 Penfolds Magill Estate",ll:[-34.92158,138.67926],q:"Penfolds Magill Estate, 78 Penfold Rd, Magill SA"}
});

DAYS.push(
{id:"adl1",city:"adl",tab:"12/5 到阿德莱德",date:"12/5",wk:"周六",color:"#7B4FA0",title:"到达阿德莱德",
 sum:"从凯恩斯飞过来，落地打车去住处。落地早的话，去中央市场看看（周六开到下午 3 点左右，周日、周一不开）。",
 chips:["机场到市区打车约 15–20 分钟","住处待定（要有厨房）"],
 notes:[["blue","住处还没订，地图上的“家”先放在市中心 Victoria Square 一带。12/6 晚上要在家做饭，订带厨房的公寓。订好后把地址告诉我，路线会重新算。"]],
 items:[
  {t:"按航班",p:"a_airport",h:"抵达阿德莱德机场",d:"出来就有出租车。"},
  L("taxi","a_airport","a_home","约 15–20 分钟 · 约 7 km",""),
  {t:"入住",p:"a_home",h:"入住，放行李",d:"住处待定，地图上先放在市中心。"},
  L("walk","a_home","a_central","约 5 分钟",""),
  {t:"下午",p:"a_central",h:"中央市场 Central Market",opt:1,d:"南半球最大的室内食品市场之一，蔬果、肉、奶酪、熟食都有。周日、周一不开，想逛只能今天。",tip:"周六一般开到 15:00 左右，以官网为准"},
  L("walk","a_central","a_home","约 5 分钟","")
 ]},
{id:"adl2",city:"adl",date:"12/6",wk:"周日",color:"#2E8B57",title:"Farmers' Market 买菜 → 逛市区 → 在家做饭",
 sum:"上午去 Wayville 的 Farmers' Market 买菜（中央市场周日不开），回家放好；下午在市区走走：Rundle Mall、North Terrace 的美术馆和博物馆、植物园、托伦斯河边；晚上在家一起做饭。",
 chips:["打车 ×2","步行约 4–5 km","美术馆、博物馆、植物园免费"],
 notes:[["blue","Farmers' Market 每周日上午开，大约 8:30–12:30（这是 2024 年的资料），去之前在官网确认。带购物袋。"]],
 items:[
  {t:"08:30",p:"a_home",h:"早餐",d:"带购物袋。"},
  L("taxi","a_home","a_farmers","约 10 分钟 · 约 3 km",""),
  {t:"09:00",p:"a_farmers",h:"Adelaide Farmers' Market",d:"本地蔬菜、水果、肉、海鲜、面包、奶酪，买晚上做饭的菜。",tip:"周日上午开，约 8:30–12:30，以官网为准"},
  L("taxi","a_farmers","a_home","约 10 分钟",""),
  {t:"11:30",p:"a_home",h:"回家放菜，吃午饭",d:""},
  L("walk","a_home","a_rundle","约 12 分钟",""),
  {t:"13:30",p:"a_rundle",h:"Rundle Mall 步行街",d:"阿德莱德的主要购物街，有百货和各种小店。"},
  L("walk","a_rundle","a_gallery","约 6 分钟",""),
  {t:"14:30",p:"a_gallery",h:"North Terrace：美术馆 / 博物馆",d:"南澳美术馆和南澳博物馆挨着，都免费，挑一个看看。"},
  L("walk","a_gallery","a_botanic","约 10 分钟",""),
  {t:"15:30",p:"a_botanic",h:"阿德莱德植物园",d:"免费，树荫多，有维多利亚式的大温室。"},
  L("walk","a_botanic","a_river","约 20 分钟",""),
  {t:"16:30",p:"a_river",h:"托伦斯河边散步",d:"Festival Centre 和 Elder Park 一带的河边步道。"},
  L("walk","a_river","a_home","约 20 分钟","","","累了就打车，约 5 分钟"),
  {t:"17:30",p:"a_home",h:"在家一起做饭",d:""}
 ]},
{id:"adl3",city:"adl",date:"12/7",wk:"周一",color:"#8E2C48",title:"奔富酒庄 Penfolds Magill Estate",
 sum:"去奔富的发源地 Magill Estate，离市区约 15 分钟车程：酒窖导览、品酒，可以在酒庄餐厅吃午饭。品酒后不开车，来回打车。",
 chips:["打车 ×2（约 15–20 分钟）","每天 10:00–17:00","导览和品酒要预约"],
 notes:[["blue","要提前在奔富官网预约导览 / 品酒，时间以预约为准。巴罗萨谷那家酒窖，奔富官网有一页说 2025 年 6 月已关闭，而且离市区约 1.5 小时车程，所以去 Magill Estate。"]],
 items:[
  {t:"10:00",p:"a_home",h:"早餐，出发",d:""},
  L("taxi","a_home","a_penfolds","约 15–20 分钟 · 约 9 km",""),
  {t:"按预约",p:"a_penfolds",h:"奔富 Penfolds Magill Estate",d:"老酒窖、葡萄园，导览后品酒。可以在酒庄的餐厅 / 小馆吃午饭（要预约）。",tip:"官网：每天 10:00–17:00；导览、品酒、用餐都以预约为准"},
  L("taxi","a_penfolds","a_home","约 15–20 分钟",""),
  {t:"下午",p:"a_home",h:"回市区休息",d:"明天飞墨尔本，晚上收拾行李。"}
 ]},
{id:"adl4",city:"adl",date:"12/8",wk:"周二",color:"#B0563A",title:"退房，飞墨尔本",
 sum:"按航班时间退房、打车去机场，飞墨尔本（约 1 小时 15 分钟）。",
 chips:["机场离市区打车约 15–20 分钟"],
 items:[
  {t:"按航班",p:"a_home",h:"收拾、退房",d:"退房时间以住处为准，国内航班一般提前 1 小时到机场。"},
  L("taxi","a_home","a_airport","约 15–20 分钟 · 约 7 km","按航班提前出发"),
  {t:"按航班",p:"a_airport",h:"飞墨尔本",d:"去墨尔本。"}
 ]}
);
