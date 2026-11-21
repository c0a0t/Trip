/* 凯恩斯 11/29–12/2：用户给的安排是
     29 号：当天到达 / 30 号：大堡礁出海一日游（报一日团玩一天）/ 1 号：热带雨林小火车（一日团玩一天）/ 2 号：返程，去阿德莱德
   每天的细节按常见一日团的做法补全：时间都是常见时间，以所报的团为准；住处还没定，“家”先放在市中心。
   坐标在 geo.json 里核准（build/places.py），路线在 routes.json（build/routes.py）。 */
Object.assign(P,{
 c_airport:{n:"凯恩斯机场（国内航站楼）",ll:[-16.8749,145.7522],q:"Cairns Airport Domestic Terminal"},
 c_home:{n:"凯恩斯住处（待定 · 先放市中心）",ll:[-16.9208,145.7776],q:"City Place, Cairns City QLD",home:1},
 c_lagoon:{n:"Esplanade 海滨泳池 + 夜市",ll:[-16.9196,145.7780],q:"Cairns Esplanade Lagoon"},
 c_reeffleet:{n:"Reef Fleet 码头",ll:[-16.9217,145.7804],q:"Reef Fleet Terminal, Cairns"},
 c_reef:{n:"外堡礁浮台（示意 · Moore Reef 一带）",ll:[-16.868,146.208],q:"Moore Reef, Great Barrier Reef"},
 c_cnsstn:{n:"Cairns 火车站",ll:[-16.9257,145.7713],q:"Cairns Railway Station, Bunda St"},
 c_barron:{n:"Barron Falls 站（看瀑布）",ll:[-16.8364,145.6430],q:"Barron Falls Station, Kuranda"},
 c_kuranda:{n:"Kuranda 火车站",ll:[-16.8185,145.6391],q:"Kuranda Railway Station"},
 c_kvillage:{n:"Kuranda 雨林小镇（市集）",ll:[-16.8194,145.6329],q:"Kuranda Heritage Markets"},
 c_skyk:{n:"Skyrail 缆车 Kuranda 站",ll:[-16.8191,145.6391],q:"Skyrail Rainforest Cableway Kuranda Terminal"},
 c_skys:{n:"Skyrail 缆车 Smithfield 站（山脚）",ll:[-16.8477,145.6951],q:"Skyrail Smithfield Terminal"}
});
Object.assign(MODES,{
 boat:{n:"出海游船",ic:"🛥️",c:"#0E6FA8",dash:"",w:4},
 cable:{n:"缆车",ic:"🚡",c:"#B5487A",dash:"",w:4}
});
// boat / cable 在 Google 地图里没有对应出行方式，不给导航链接

DAYS.push(
{id:"cns1",city:"cairns",tab:"11/29 到凯恩斯",date:"11/29",wk:"周日",color:"#C8901A",title:"到达凯恩斯",
 sum:"当天到达。从悉尼飞过来约 3 小时，落地打车去住处；傍晚有精神就去海滨走走。",
 chips:["机场到市区打车约 15 分钟","住处待定"],
 notes:[["blue","住处还没订，地图上的“家”先放在市中心（City Place 一带）。订好后把地址告诉我，路线会重新算。"]],
 items:[
  {t:"按航班",p:"c_airport",h:"抵达凯恩斯机场",d:"国内航站楼，出来就有出租车。"},
  L("taxi","c_airport","c_home","约 15 分钟 · 约 7 km",""),
  {t:"入住",p:"c_home",h:"入住，放行李",d:"住处待定，地图上先放在市中心。"},
  L("walk","c_home","c_lagoon","约 5 分钟",""),
  {t:"傍晚",p:"c_lagoon",h:"Esplanade 海滨 + 夜市",opt:1,d:"海边的免费人造泳池和草坪，旁边是夜市，可以顺便吃晚饭。凯恩斯海里有水母和鳄鱼，别下海游泳。累了就不去。",tip:"夜市一般傍晚开到晚上 11 点左右，以现场为准"},
  L("walk","c_lagoon","c_home","约 5 分钟","")
 ]},
{id:"cns2",city:"cairns",date:"11/30",wk:"周一",color:"#0E7C86",title:"大堡礁出海一日游",
 sum:"去大堡礁出海一日游（报一日团玩一天）。下面按常见的外堡礁浮台团排时间，以所报的团为准。",
 chips:["船程单程约 1.5 小时","浮潜 / 玻璃底船 / 半潜艇","时间以团为准"],
 notes:[["blue","选团时看：① 去外堡礁（Outer Reef）还是绿岛，外堡礁珊瑚更好、船程更长；② 有没有浮台（pontoon），浮台上有玻璃底船、半潜艇，不下水也能看珊瑚；③ 是否含午餐和浮潜装备；④ 有没有中文讲解。"],
        ["","11 月到次年 5 月是水母季，下水要穿防蛰服（stinger suit），一般团里提供。容易晕船的提前半小时吃晕船药，船上一般也有卖。"]],
 items:[
  {t:"07:00",p:"c_home",h:"早餐",d:"带泳衣、毛巾、帽子、防晒、晕船药。"},
  L("walk","c_home","c_reeffleet","约 5 分钟",""),
  {t:"07:30",p:"c_reeffleet",h:"Reef Fleet 码头报到上船",d:"凯恩斯出海的船基本都从这里出发，到所报公司的柜台报名字换船票。",tip:"常见 8:00 前后开船，报到时间以团为准"},
  L("boat","c_reeffleet","c_reef","约 1.5 小时",""),
  {t:"约 09:30",p:"c_reef",h:"大堡礁：浮潜 / 玻璃底船 / 半潜艇",d:"在浮台或礁区停 4–5 小时：会游泳的浮潜，不会游泳的坐玻璃底船、半潜艇看珊瑚和鱼。中午在船上吃午餐。",tip:"地图上的位置是示意（常见去 Moore Reef 一带），去哪片礁以所报的团为准"},
  L("boat","c_reef","c_reeffleet","约 1.5 小时",""),
  {t:"约 17:00",p:"c_reeffleet",h:"回到码头",d:""},
  L("walk","c_reeffleet","c_home","约 5 分钟",""),
  {t:"17:30",p:"c_home",h:"回住处休息",d:"出海一天很累，晚饭在附近随便吃，早点休息。"}
 ]},
{id:"cns3",city:"cairns",date:"12/1",wk:"周二",color:"#5B8C2A",title:"热带雨林小火车 + 缆车",
 sum:"去凯恩斯热带雨林小火车（一日团玩一天）。常见玩法：坐 Kuranda 观光火车上山，在雨林小镇逛半天，再坐 Skyrail 缆车从雨林上空下山，团车送回。时间以团为准。",
 chips:["火车约 2 小时","缆车约 1.5 小时（含中途两站）","步行少"],
 notes:[["blue","火车途中在 Barron Falls 站停十来分钟看瀑布；12 月初刚进雨季，水量看天。缆车中途 Red Peak、Barron Falls 两站可以下车走一小段木栈道，再上车继续。"]],
 items:[
  {t:"07:30",p:"c_home",h:"早餐",d:"带薄外套（山上稍凉）、防蚊液、雨具。"},
  L("taxi","c_home","c_cnsstn","约 5 分钟","很多团会到住处接，以团为准"),
  {t:"08:15",p:"c_cnsstn",h:"Cairns 火车站上观光火车",d:"Kuranda Scenic Railway，老式观光列车，沿山谷、瀑布慢慢爬上山。",tip:"常见 8:30 / 9:30 发车（Freshwater 站也能上车），以团为准"},
  L("train","c_cnsstn","c_barron","约 1.5 小时","经 Freshwater 站上山"),
  {t:"约 10:00",p:"c_barron",h:"Barron Falls 站：下车看瀑布",d:"火车停十来分钟，在站台旁的观景台看 Barron 瀑布。"},
  L("train","c_barron","c_kuranda","约 15 分钟",""),
  {t:"约 10:30",p:"c_kuranda",h:"到 Kuranda 站",d:"站台被热带植物包着，很出片。出站沿坡道走进小镇。"},
  L("walk","c_kuranda","c_kvillage","约 10 分钟 · 上坡",""),
  {t:"10:45",p:"c_kvillage",h:"Kuranda 雨林小镇",d:"逛小镇市集（Heritage Markets / Original Markets），吃午饭。体力好可以去蝴蝶园、鸟园或考拉园（门票另算，有的团已含）。"},
  L("walk","c_kvillage","c_skyk","约 10 分钟",""),
  {t:"约 14:30",p:"c_skyk",h:"坐 Skyrail 缆车下山",d:"缆车从雨林树冠上空过，全长约 7.5 km。",tip:"中途 Barron Falls、Red Peak 两站可以下车走木栈道，再上车继续"},
  L("cable","c_skyk","c_skys","约 1.5 小时（含中途两站）",""),
  {t:"约 16:00",p:"c_skys",h:"Smithfield 缆车站（山脚）",d:"团车在这里接，送回市区。"},
  L("coach","c_skys","c_home","约 25 分钟",""),
  {t:"约 17:00",p:"c_home",h:"回住处",d:"明天要走，晚上收拾行李。"}
 ]},
{id:"cns4",city:"cairns",date:"12/2",wk:"周三",color:"#B0563A",title:"返程，去阿德莱德",
 sum:"返程，去阿德莱德。按航班时间退房、打车去机场。",
 chips:["机场离市区打车约 15 分钟"],
 items:[
  {t:"按航班",p:"c_home",h:"收拾、退房",d:"退房时间以住处为准，国内航班一般提前 1 小时到机场。"},
  L("taxi","c_home","c_airport","约 15 分钟 · 约 7 km","按航班提前出发"),
  {t:"按航班",p:"c_airport",h:"飞阿德莱德",d:"去阿德莱德。"}
 ]}
);
