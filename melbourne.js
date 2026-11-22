/* 墨尔本 12/8–12/11。用户的安排：12/8 从阿德莱德飞到 / 12/9 大洋路十二门徒 / 12/10 普芬比利蒸汽小火车 / 12/11 从墨尔本返程回家（机票还没订）
   大洋路按常见一日团排（去程走海岸、回程走内陆），时间以所报的团为准；普芬比利班次以官网为准。
   住处还没定，“家”先放在市中心。坐标在 geo.json（build/places.py），路线在 routes.json（build/routes.py）。 */
Object.assign(P,{
 m_airport:{n:"墨尔本机场（T1–T3）",ll:[-37.67065,144.8503],q:"Melbourne Airport"},
 m_home:{n:"墨尔本住处（待定 · 先放市中心）",ll:[-37.81492,144.96685],q:"Melbourne Town Hall, Swanston St",home:1},
 m_meet:{n:"大洋路团集合点（示例 · Federation Square）",ll:[-37.81774,144.96916],q:"Federation Square, Melbourne"},
 m_arch:{n:"大洋路纪念拱门 Memorial Arch",ll:[-38.47204,144.04458],q:"Great Ocean Road Memorial Arch, Eastern View VIC"},
 m_apollo:{n:"Apollo Bay 小镇（午饭）",ll:[-38.75474,143.66915],q:"Apollo Bay VIC"},
 m_12a:{n:"十二门徒 Twelve Apostles",ll:[-38.66428,143.1038],q:"The Twelve Apostles, Princetown VIC"},
 m_lochard:{n:"Loch Ard Gorge 峡湾",ll:[-38.64641,143.07033],q:"Loch Ard Gorge, Port Campbell VIC"},
 m_flinders:{n:"Flinders Street 火车站",ll:[-37.81842,144.96648],q:"Flinders Street Station, Melbourne"},
 m_belgrave:{n:"Belgrave 火车站（市郊线终点）",ll:[-37.90901,145.35525],q:"Belgrave Station, Belgrave VIC"},
 m_pbbel:{n:"普芬比利 Belgrave 站",ll:[-37.90768,145.35657],q:"Puffing Billy Railway, Belgrave Station"},
 m_lakeside:{n:"普芬比利 Lakeside 站（Emerald Lake）",ll:[-37.9304,145.45965],q:"Puffing Billy Lakeside Station, Emerald VIC"}
});
Object.assign(MODES,{
 steam:{n:"蒸汽小火车",ic:"🚂",c:"#6D4C41",dash:"",w:4}
});

DAYS.push(
{id:"mel1",city:"mel",tab:"12/8 到墨尔本",date:"12/8",wk:"周二",color:"#C8901A",title:"到达墨尔本",
 sum:"从阿德莱德飞过来，落地去住处，晚上早点休息，明天大洋路一日游要早起。",
 chips:["机场到市区打车约 30 分钟","住处待定"],
 notes:[["blue","住处还没订，地图上的“家”先放在市中心。订好后把地址告诉我，路线会重新算。"]],
 items:[
  {t:"按航班",p:"m_airport",h:"抵达墨尔本机场",d:"出来就有出租车；也可以坐 SkyBus 机场大巴到市区 Southern Cross 站。"},
  L("taxi","m_airport","m_home","约 30 分钟 · 约 23 km",""),
  {t:"入住",p:"m_home",h:"入住，早点休息",d:"住处待定，地图上先放在市中心。"}
 ]},
{id:"mel2",city:"mel",date:"12/9",wk:"周三",color:"#0E6FA8",title:"大洋路 + 十二门徒一日游",
 sum:"报一日团：早上出发，沿大洋路海岸往西开，经过纪念拱门、Apollo Bay，下午到十二门徒和 Loch Ard Gorge，回程走内陆公路，晚上回到墨尔本。一整天大多在车上。时间是常见一日团的时间，以所报的团为准。",
 chips:["全程约 12–13 小时","时间以团为准"],
 notes:[["blue","选团时看：① 是不是去程走海岸大洋路、回程走内陆（比较快）；② 停哪些点：纪念拱门、Kennett River 看野生考拉、Apollo Bay 午饭、十二门徒、Loch Ard Gorge；③ 集合点离住处近不近；④ 有没有中文导游。自己开车单程三个多小时，而且靠左行驶，不建议。"],
        ["","海边风大，带件防风外套。前一天刚飞到墨尔本，晚上早点睡。"]],
 items:[
  {t:"06:45",p:"m_home",h:"早餐",d:"带防风外套、水、零食。"},
  L("walk","m_home","m_meet","约 5 分钟","集合点以团为准"),
  {t:"07:00",p:"m_meet",h:"集合出发",d:"地图上的位置仅为示意（很多团在 Federation Square 一带集合），以你报的团为准。"},
  N("coach","m_meet","m_arch","约 2.5 小时","经 Geelong、Torquay"),
  {t:"约 09:45",p:"m_arch",h:"大洋路纪念拱门",d:"大洋路的标志，拍照打卡。"},
  N("coach","m_arch","m_apollo","约 1.5 小时","沿海岸开，很多团中途在 Kennett River 停下看野生考拉"),
  {t:"约 12:00",p:"m_apollo",h:"Apollo Bay：午饭",d:"海边小镇，午饭一般自理。"},
  N("coach","m_apollo","m_12a","约 1.5–2 小时","穿过 Otway 雨林"),
  {t:"约 15:00",p:"m_12a",h:"十二门徒 Twelve Apostles",d:"海里的石灰岩柱，从观景台步道看。"},
  N("coach","m_12a","m_lochard","约 5 分钟",""),
  {t:"约 16:00",p:"m_lochard",h:"Loch Ard Gorge 峡湾",d:"两边是悬崖的小海湾，有步道下到沙滩。"},
  N("coach","m_lochard","m_meet","约 3.5 小时","回程走内陆公路，比海岸路快"),
  {t:"约 20:00",p:"m_meet",h:"回到市区散团",d:""},
  L("walk","m_meet","m_home","约 5 分钟",""),
  {t:"20:30",p:"m_home",h:"回住处休息",d:""}
 ]},
{id:"mel3",city:"mel",date:"12/10",wk:"周四",color:"#6D4C41",title:"普芬比利蒸汽小火车",
 sum:"坐市郊火车到 Belgrave，换乘普芬比利（Puffing Billy）百年蒸汽小火车，穿过丹德农山区的森林和木栈桥，到 Lakeside 站（Emerald Lake）吃午饭、散步，再坐回来。",
 chips:["市郊火车单程约 1 小时 10 分钟","蒸汽火车单程约 1 小时","票要提前在官网订"],
 notes:[["blue","普芬比利的班次和票价以官网为准，热门班次会满，提前订。12 月是夏天，遇到全面禁火日（Total Fire Ban），蒸汽车头可能换成柴油车头或调整班次，出发前一天看官网通知。"],
        ["","也可以报一日团（常和丹德农山区一起玩），省去换车。墨尔本坐火车用 myki 卡，在车站机器买、充值。"]],
 items:[
  {t:"08:30",p:"m_home",h:"早餐",d:""},
  L("walk","m_home","m_flinders","约 8 分钟",""),
  {t:"09:00",p:"m_flinders",h:"Flinders Street 站坐 Belgrave 线",d:"坐到终点 Belgrave。"},
  L("train","m_flinders","m_belgrave","约 1 小时 10 分钟","Belgrave 线，终点站下车"),
  {t:"约 10:15",p:"m_belgrave",h:"Belgrave 站",d:"出站走几分钟到普芬比利的 Belgrave 站。"},
  L("walk","m_belgrave","m_pbbel","约 5 分钟",""),
  {t:"约 10:30",p:"m_pbbel",h:"普芬比利 Belgrave 站上车",d:"百年蒸汽小火车，木制车厢，穿过森林和 Monbulk Creek 木栈桥。",tip:"发车时间以官网时刻表为准"},
  N("steam","m_pbbel","m_lakeside","约 1 小时",""),
  {t:"约 11:30",p:"m_lakeside",h:"Lakeside 站：Emerald Lake 午饭、散步",d:"湖边公园，有咖啡馆和草坪，也可以带午饭野餐。"},
  N("steam","m_lakeside","m_pbbel","约 1 小时","坐回 Belgrave"),
  {t:"约 14:30",p:"m_pbbel",h:"回到 Belgrave",d:""},
  L("walk","m_pbbel","m_belgrave","约 5 分钟",""),
  L("train","m_belgrave","m_flinders","约 1 小时 10 分钟",""),
  {t:"约 16:00",p:"m_flinders",h:"回到市区",d:""},
  L("walk","m_flinders","m_home","约 8 分钟",""),
  {t:"16:30",p:"m_home",h:"回住处休息",d:"明天返程，晚上收拾行李。"}
 ]},
{id:"mel4",city:"mel",date:"12/11",wk:"周五",color:"#5B6770",title:"退房，返程回家",
 sum:"从墨尔本返程回家。返程机票还没订，具体时间按航班：退房、打车去机场。",
 chips:["机票待定","机场离市区打车约 30 分钟"],
 notes:[["blue","返程机票还没订，订好后把航班时间告诉我，这一天的时间会跟着改。"]],
 items:[
  {t:"按航班",p:"m_home",h:"收拾、退房",d:"退房时间以住处为准，国际航班一般提前 3 小时到机场。"},
  L("taxi","m_home","m_airport","约 30 分钟 · 约 23 km","按航班提前出发"),
  {t:"按航班",p:"m_airport",h:"返程回家",d:"国际航班在 T2 航站楼，以机票为准。"}
 ]}
);
