/* 凯恩斯 11/30–12/5。用户的安排：
     11/30 从悉尼飞到 / 12/1 大堡礁（飞猪：Reef Magic 船去飞回 + 浮潜 + 自助餐）/ 12/2 库兰达（飞猪：A 缆车 + 火车 + 雨林 + 接送）/
     12/3 海钓（全天出海或半天河口，待定）/ 12/4 休整 / 12/5 飞阿德莱德
   时间：Reef Magic 9:00 开船、库兰达下山火车 14:45 / 15:30 来自官网；其余是常见时间，以确认单为准。住处还没定，“家”先放在市中心。
   坐标在 geo.json 里核准（build/places.py），路线在 routes.json（build/routes.py）。 */
Object.assign(P,{
 c_airport:{n:"凯恩斯机场（国内航站楼）",ll:[-16.8749,145.7522],q:"Cairns Airport Domestic Terminal"},
 c_home:{n:"凯恩斯住处（待定 · 先放市中心）",ll:[-16.9208,145.7776],q:"City Place, Cairns City QLD",home:1},
 c_lagoon:{n:"Esplanade 海滨泳池 + 夜市",ll:[-16.9196,145.7780],q:"Cairns Esplanade Lagoon"},
 c_reeffleet:{n:"Reef Fleet 码头",ll:[-16.9217,145.7804],q:"Reef Fleet Terminal, Cairns"},
 c_reef:{n:"Reef Magic 浮台（示意 · Moore Reef 一带）",ll:[-16.868,146.208],q:"Moore Reef, Great Barrier Reef"},
 c_heli:{n:"直升机降落点（示意 · 凯恩斯机场一带）",ll:[-16.87172,145.7376],q:"Nautilus Aviation, Cairns"},
 c_cnsstn:{n:"Cairns 火车站",ll:[-16.9257,145.7713],q:"Cairns Railway Station, Bunda St"},
 c_kuranda:{n:"Kuranda 火车站",ll:[-16.8185,145.6391],q:"Kuranda Railway Station"},
 c_kvillage:{n:"Kuranda 雨林小镇（市集）",ll:[-16.8194,145.6329],q:"Kuranda Heritage Markets"},
 c_skyk:{n:"Skyrail 缆车 Kuranda 站",ll:[-16.8191,145.6391],q:"Skyrail Rainforest Cableway Kuranda Terminal"},
 c_skys:{n:"Skyrail 缆车 Smithfield 站（山脚）",ll:[-16.8477,145.6951],q:"Skyrail Smithfield Terminal"},
 c_rainf:{n:"雨林公园 Rainforestation",ll:[-16.82368,145.65206],q:"Rainforestation Nature Park, Kuranda"},
 c_marina:{n:"Marlin Marina（钓鱼船码头 · 集合点待定）",ll:[-16.9214,145.78131],q:"Marlin Marina, Cairns"},
 c_rustys:{n:"Rusty's Markets 农贸市场",ll:[-16.92444,145.77508],q:"Rusty's Markets, Cairns"},
 c_botanic:{n:"凯恩斯植物园",ll:[-16.9001,145.75043],q:"Cairns Botanic Gardens"}
});
Object.assign(MODES,{
 boat:{n:"出海游船",ic:"🛥️",c:"#0E6FA8",dash:"",w:4},
 cable:{n:"缆车",ic:"🚡",c:"#B5487A",dash:"",w:4},
 heli:{n:"直升机",ic:"🚁",c:"#D35400",dash:"2 8",w:3.5}
});
// boat / cable / heli 在 Google 地图里没有对应出行方式，不给导航链接

DAYS.push(
{id:"cns1",city:"cairns",tab:"11/30 到凯恩斯",date:"11/30",wk:"周一",color:"#C8901A",title:"到达凯恩斯",
 sum:"当天到达。从悉尼飞过来约 3 小时，落地打车去住处；傍晚有精神就去海滨走走。",
 chips:["机场到市区打车约 15 分钟","住处待定"],
 notes:[["blue","住处还没订，地图上的“家”先放在市中心（City Place 一带）。订好后把地址告诉我，路线会重新算。凯恩斯住 5 晚（11/30–12/5）。"]],
 items:[
  {t:"按航班",p:"c_airport",h:"抵达凯恩斯机场",d:"国内航站楼，出来就有出租车。"},
  L("taxi","c_airport","c_home","约 15 分钟 · 约 7 km",""),
  {t:"入住",p:"c_home",h:"入住，放行李",d:"住处待定，地图上先放在市中心。"},
  L("walk","c_home","c_lagoon","约 5 分钟",""),
  {t:"傍晚",p:"c_lagoon",h:"Esplanade 海滨 + 夜市",opt:1,d:"海边的免费人造泳池和草坪，旁边是夜市，可以顺便吃晚饭。凯恩斯海里有水母和鳄鱼，别下海游泳。累了就不去。",tip:"夜市一般傍晚开到晚上 11 点左右，以现场为准"},
  L("walk","c_lagoon","c_home","约 5 分钟","")
 ]},
{id:"cns2",city:"cairns",date:"12/1",wk:"周二",color:"#0E7C86",title:"大堡礁：Reef Magic 坐船去、直升机飞回",
 sum:"飞猪订的 Reef Magic（魔幻丽礁号）“船去飞回 + 浮潜 + 自助餐”：上午从 Reef Fleet 码头坐高速双体船去外堡礁的浮台，浮潜、坐玻璃底船、吃自助午餐，下午坐直升机飞回凯恩斯。不含接送。",
 chips:["9:00 开船（官网）","船程约 1.5–2 小时","直升机回程约 25–30 分钟","飞猪 ¥3020/人"],
 notes:[["blue","下单前问商家：① 几点、在哪个码头报到；② 直升机几点从浮台起飞、降落在哪里，降落后怎么回市区；③ 天气不好船不开或直升机不飞怎么处理；④ 价格里含不含大堡礁环境管理费（EMC）和燃油附加费。"],
        ["","退改：出发前 10 天以上取消不扣钱，1–9 天内取消全额不退。11 月到次年 5 月是水母季，下水穿防蛰服（一般浮台提供）；容易晕船的提前半小时吃晕船药。12/4 是休整日，出海如果因天气取消，可以问能不能改到那天。"]],
 items:[
  {t:"07:30",p:"c_home",h:"早餐",d:"带泳衣、毛巾、帽子、防晒、晕船药。"},
  L("walk","c_home","c_reeffleet","约 5 分钟",""),
  {t:"08:15",p:"c_reeffleet",h:"Reef Fleet 码头报到",d:"到 Reef Magic 柜台报名字、换船票。",tip:"官网显示 9:00 开船；报到时间以确认单为准"},
  L("boat","c_reeffleet","c_reef","约 1.5–2 小时","高速双体船，船上有空调大厅"),
  {t:"约 11:00",p:"c_reef",h:"Reef Magic 浮台：浮潜 / 玻璃底船 / 午餐",d:"浮潜、坐玻璃底船看珊瑚和鱼，中午吃自助午餐。深潜等项目另付费。玻璃底船按点开，到了先问好时间。",tip:"地图上的位置是示意（Moore Reef 一带）"},
  L("heli","c_reef","c_heli","约 25–30 分钟","起飞时间按商家安排；路线示意"),
  {t:"下午",p:"c_heli",h:"直升机降落（示意位置）",d:"从空中看大堡礁和海岸线。降落点以商家为准，地图上先放在凯恩斯机场一带。"},
  L("taxi","c_heli","c_home","约 15 分钟",""),
  {t:"傍晚",p:"c_home",h:"回住处休息",d:"出海一天很累，晚饭在附近随便吃，早点休息。"}
 ]},
{id:"cns3",city:"cairns",date:"12/2",wk:"周三",color:"#5B8C2A",title:"库兰达：缆车上山 → 雨林公园 → 火车下山",
 sum:"飞猪订的库兰达一日游（A 套餐：缆车 + 火车 + 雨林 + 接送）：酒店接，坐 Skyrail 缆车从雨林上空上山，去雨林公园（Rainforestation），逛库兰达小镇，下午坐观光火车下山，团车送回。中文导游兼司机。",
 chips:["缆车约 1.5 小时（含中途两站）","火车约 2 小时","午餐自理","飞猪 ¥1100/人 + 司导费 A$5/人"],
 notes:[["blue","商家默认缆车上山、火车下山；当天缆车满位会换成火车上山、缆车下山。拼车团，时间固定，以确认单为准。下单时填凯恩斯住处地址，问好几点来接。"],
        ["","司导服务费每人 A$5，现金付给司机。退改：出发前 5 天以上（11/27 之前）取消不扣钱。12 月初刚进雨季，带雨具和防蚊液。"]],
 items:[
  {t:"07:30",p:"c_home",h:"早餐",d:"带薄外套（山上稍凉）、防蚊液、雨具、零钱。"},
  N("coach","c_home","c_skys","约 25 分钟","酒店接，接人时间以确认单为准"),
  {t:"约 08:30",p:"c_skys",h:"Skyrail 缆车 Smithfield 站（山脚）",d:"坐缆车从雨林树冠上空上山，全长约 7.5 km。",tip:"中途 Red Peak、Barron Falls 两站可以下车走木栈道、看瀑布，再上车继续"},
  L("cable","c_skys","c_skyk","约 1.5 小时（含中途两站）",""),
  {t:"约 10:00",p:"c_skyk",h:"Skyrail Kuranda 站",d:"团车接去雨林公园。"},
  N("coach","c_skyk","c_rainf","约 5 分钟",""),
  {t:"约 10:30",p:"c_rainf",h:"雨林公园 Rainforestation",d:"坐二战水陆两栖车（Army Duck）穿雨林、下河；看原住民表演；小动物园里看袋鼠、考拉。",tip:"抱考拉合影要另付费，想抱的提前问"},
  N("coach","c_rainf","c_kvillage","约 5 分钟",""),
  {t:"约 13:00",p:"c_kvillage",h:"库兰达小镇：午饭 + 逛市集",d:"午餐自理。小镇有 Heritage Markets、Original Markets，还有蝴蝶园、鸟园（门票另算）。"},
  L("walk","c_kvillage","c_kuranda","约 10 分钟",""),
  {t:"约 15:00",p:"c_kuranda",h:"Kuranda 火车站上观光火车",d:"老式观光火车下山，沿山谷、瀑布慢慢开。",tip:"下午两班：14:45、15:30（官网时刻），坐哪班以确认单为准"},
  N("train","c_kuranda","c_cnsstn","约 2 小时","经 Freshwater 站；有的团在 Freshwater 站下车换团车"),
  {t:"约 17:25",p:"c_cnsstn",h:"到凯恩斯火车站",d:"团车送回住处。"},
  N("coach","c_cnsstn","c_home","约 5 分钟",""),
  {t:"约 17:45",p:"c_home",h:"回住处",d:""}
 ]},
{id:"cnsfish",city:"cairns",date:"12/3",wk:"周四",color:"#2F6EA3",title:"海钓（全天出海 / 半天河口，待定）",
 sum:"这天就是钓鱼：全天出海钓珊瑚礁鱼，还是半天在河口钓，还没定。很多钓鱼船从市中心的 Marlin Marina 出发（地图上先放在这里），定了之后按实际集合点改。",
 chips:["还没订","钓具、鱼饵一般船上提供"],
 notes:[["blue","两种选法：① 全天出海钓：去外海钓东星斑（Coral Trout）、红鲷（Red Emperor）等，鱼好、个头大，但浪大容易晕船，而且 12/1 刚坐过一天船；② 半天河口 / 红树林钓：在 Trinity Inlet，水面平静、基本不晕船，适合新手，能钓红树林笛鲷（Mangrove Jack）等。12/1 有人晕船的话选河口钓。"],
        ["","12 月是尖吻鲈（Barramundi）禁渔期（昆士兰东海岸 11/1 中午到 2/1 中午），钓上来放回去也不行，写着“钓 Barra”的项目这段时间做不了。在昆士兰海钓不用办钓鱼证；钓到的鱼船家一般会帮忙处理。"]],
 items:[
  {t:"按团",p:"c_home",h:"早餐",d:"带防晒、帽子、晕船药。"},
  L("walk","c_home","c_marina","约 8 分钟",""),
  {t:"按团",p:"c_marina",h:"海钓出发（集合点待定）",d:"全天团一般早上出发、下午回；半天团分上午、下午场。集合点以所订的为准。"},
  L("walk","c_marina","c_home","约 8 分钟",""),
  {t:"傍晚",p:"c_home",h:"回住处",d:"钓到的鱼可以问附近餐厅能不能代做。"}
 ]},
{id:"cnsrest",city:"cairns",date:"12/4",wk:"周五",color:"#8C6BB1",title:"休整日",
 sum:"不安排行程，睡到自然醒。想出门的话市区有几个轻松的地方，都不用预约。12/1 出海如果因天气取消，这天可以当备用日。",
 chips:["全部可选","步行少"],
 items:[
  {t:"上午",p:"c_home",h:"睡到自然醒",d:""},
  L("walk","c_home","c_rustys","约 8 分钟",""),
  {t:"上午",p:"c_rustys",h:"Rusty's Markets 农贸市场",opt:1,d:"凯恩斯本地的农贸市场，热带水果、咖啡、小吃很多。",tip:"周五至周日开，以官网时间为准"},
  L("walk","c_rustys","c_home","约 8 分钟",""),
  L("taxi","c_home","c_botanic","约 10 分钟 · 约 4 km",""),
  {t:"下午",p:"c_botanic",h:"凯恩斯植物园",opt:1,d:"平路、树荫多，热带植物和温室，适合慢慢走。"},
  L("taxi","c_botanic","c_lagoon","约 10 分钟",""),
  {t:"傍晚",p:"c_lagoon",h:"Esplanade 海滨泳池",opt:1,d:"市中心免费的露天泳池，有救生员；12 月是水母季，在这里游泳比去海里安全。旁边就是夜市。"},
  L("walk","c_lagoon","c_home","约 5 分钟",""),
  {t:"晚上",p:"c_home",h:"收拾行李",d:"明天飞阿德莱德。"}
 ]},
{id:"cns4",city:"cairns",date:"12/5",wk:"周六",color:"#B0563A",title:"退房，飞阿德莱德",
 sum:"按航班时间退房、打车去机场，飞阿德莱德。",
 chips:["机场离市区打车约 15 分钟"],
 items:[
  {t:"按航班",p:"c_home",h:"收拾、退房",d:"退房时间以住处为准，国内航班一般提前 1 小时到机场。"},
  L("taxi","c_home","c_airport","约 15 分钟 · 约 7 km","按航班提前出发"),
  {t:"按航班",p:"c_airport",h:"飞阿德莱德",d:"去阿德莱德。"}
 ]}
);
