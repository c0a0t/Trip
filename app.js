/* 悉尼行程地图：Leaflet + OSM 瓦片；路线来自构建期生成的 routes.json，坐标来自 geo.json。
   行程数据（P / DAYS / MODES / GMODE）在 data.js，原样摘自 itinerary-source.html。 */
(async function(){
"use strict";
const L=window.L; // data.js 里的路段构造函数也叫 L（全局 const），这里取回 Leaflet

/* ======================= 数据加载 ======================= */
let GEO={},ROUTES={},loadErr=null;
try{
  const [g,r]=await Promise.all(["geo.json","routes.json"].map(f=>fetch(f,{cache:"no-cache"}).then(x=>{if(!x.ok)throw new Error(f+" "+x.status);return x.json()})));
  GEO=g;ROUTES=r;
}catch(e){loadErr=e;console.warn("路线数据加载失败，退回近似折线",e)}
// 核准坐标覆盖 data.js 里的近似坐标；蓝山/机场现在是真实位置，不再是图边箭头
for(const k in GEO){ if(P[k]) P[k].ll=GEO[k].ll; }
P.echopoint={n:"Echo Point 三姐妹峰",ll:(GEO.echopoint||{ll:[-33.73224,150.31217]}).ll,q:"Echo Point Lookout, Katoomba NSW",sub:"bluemtn"};
const NO_NAV=new Set(["bluemtn"]);  // 跟团大巴段不给导航（原页面同样不给）
delete P.bluemtn.edge; delete P.airport.edge;
// 蓝山日：Echo Point 作为蓝山那一站的附属标记
const SUBS={day4:["echopoint"]};

const legKey=lg=>`${lg.mode}:${lg.from}>${lg.to}`;
const legPath=lg=>{const r=ROUTES[legKey(lg)];return r?r.coords:(lg.path||[P[lg.from].ll,P[lg.to].ll])};
const legInfo=lg=>ROUTES[legKey(lg)]||null;

/* ======================= 状态 ======================= */
const state={day:null,variant:{},sel:null,selLeg:null};
DAYS.forEach(d=>{if(d.variants)state.variant[d.id]=d.variants.def});
const dayById=id=>DAYS.find(d=>d.id===id);
const visibleItems=d=>d.items.filter(it=>{const v=it.v||it.vv;return !v||v===state.variant[d.id]});
const legsOf=d=>visibleItems(d).filter(i=>i.leg);
const stopsOf=d=>visibleItems(d).filter(i=>!i.leg);
function numbering(d){const m={};let n=0;stopsOf(d).forEach(s=>{if(P[s.p].home)return;if(!(s.p in m))m[s.p]=s.extra?"＋":String(++n)});return m}
const isNarrow=()=>window.innerWidth<=820;

/* ======================= 地图 ======================= */
const mapEl=document.getElementById("map"),mapwrap=document.getElementById("mapwrap");
const map=L.map(mapEl,{
  zoomControl:false,attributionControl:true,minZoom:9,maxZoom:19,
  maxBounds:[[-34.25,149.95],[-33.45,151.55]],maxBoundsViscosity:.8,
  zoomSnap:.25,zoomDelta:1,wheelPxPerZoomLevel:90,tapTolerance:12,bounceAtZoomLimits:false
}).setView([-33.872,151.205],13);
map.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{
  maxZoom:19,
  attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors · 路线 <a href="https://routing.openstreetmap.de/about.html" target="_blank" rel="noopener">FOSSGIS OSRM</a>'
}).addTo(map);
L.control.zoom({position:"topright",zoomInTitle:"放大",zoomOutTitle:"缩小"}).addTo(map);
// 自定义按钮：显示当天全部 / 展开地图（手机）
const Btns=L.Control.extend({options:{position:"topright"},onAdd(){
  const c=L.DomUtil.create("div","leaflet-bar");
  c.innerHTML=`<a href="#" class="ctl ctl-fit" title="显示当天全部" aria-label="显示当天全部" role="button">⤢</a><a href="#" class="ctl ctl-exp" title="展开/收起地图" aria-label="展开地图" role="button">⇕</a>`;
  L.DomEvent.disableClickPropagation(c);
  c.querySelector(".ctl-fit").onclick=e=>{e.preventDefault();fitDay()};
  c.querySelector(".ctl-exp").onclick=e=>{e.preventDefault();toggleBig()};
  return c}});
new Btns().addTo(map);

const routeLayer=L.layerGroup().addTo(map), iconLayer=L.layerGroup().addTo(map), markLayer=L.layerGroup().addTo(map);
let markers=[];   // {p, d, m(L.marker), el}
let legLines=[];  // {lg, d, latlngs, line, casing}

/* iOS Safari：地图区域内的双指手势只缩放地图，不缩放整个网页 */
["gesturestart","gesturechange","gestureend"].forEach(t=>mapwrap.addEventListener(t,e=>e.preventDefault(),{passive:false}));
mapwrap.addEventListener("touchmove",e=>{if(e.cancelable)e.preventDefault()},{passive:false});
mapwrap.addEventListener("touchstart",e=>{if(e.touches.length>1&&e.cancelable)e.preventDefault()},{passive:false});

function markerHTML(cls,bg,txt,label){
  return `<div class="mk ${cls}"><div class="pin" style="background:${bg}">${txt}</div>${label?`<span class="lbl">${label}</span>`:""}</div>`;
}
function render(){
  routeLayer.clearLayers();iconLayer.clearLayers();markLayer.clearLayers();markers=[];legLines=[];
  const single=!!state.day;
  const days=single?[dayById(state.day)]:DAYS;
  days.forEach(d=>{
    legsOf(d).forEach(lg=>{
      const m=MODES[lg.mode],info=legInfo(lg),ll=legPath(lg),schem=info&&info.kind==="schematic";
      let casing=null;
      if(single) casing=L.polyline(ll,{color:"#fff",weight:m.w+4,opacity:.9,interactive:false,lineCap:"round",lineJoin:"round"}).addTo(routeLayer);
      const line=L.polyline(ll,{color:single?m.c:d.color,weight:single?m.w+.5:3,opacity:single?(schem?.6:1):.8,
        dashArray:schem?"2 9":(m.dash||null),lineCap:"round",lineJoin:"round",interactive:false}).addTo(routeLayer);
      legLines.push({lg,d,ll,line,casing});
      if(single&&lg.mode!=="walk"){
        const mid=midpoint(ll);
        L.marker(mid,{interactive:false,keyboard:false,icon:L.divIcon({className:"",iconSize:[24,24],iconAnchor:[12,12],html:`<div class="modeic" style="border-color:${m.c}">${m.ic}</div>`})}).addTo(iconLayer);
      }
    });
  });
  const placed={};
  days.forEach(d=>{
    const num=numbering(d);
    const addMk=(p,cls,bg,txt,label,z)=>{
      const pl=P[p];
      const mk=L.marker(pl.ll,{interactive:false,keyboard:false,zIndexOffset:z||0,
        icon:L.divIcon({className:"",iconSize:[26,26],iconAnchor:[13,13],html:markerHTML(cls,bg,txt,label)})}).addTo(markLayer);
      markers.push({p,d:d.id,m:mk,get el(){return mk.getElement()}});
    };
    stopsOf(d).forEach(s=>{
      const key=d.id+s.p;if(placed[key])return;placed[key]=1;const pl=P[s.p];
      if(pl.home) addMk(s.p,"home","#1F2328","家",single?pl.n:"住处",500);
      else if(single) addMk(s.p,"",s.extra?"#9AA0A6":d.color,num[s.p],pl.n,200);
      else addMk(s.p,"small",d.color,"","",0);
    });
    // 只作为路段终点、没有停留项的地点（如机场）
    legsOf(d).forEach(lg=>{[lg.to].forEach(p=>{const key=d.id+p;if(placed[key])return;placed[key]=1;
      addMk(p,single?"sub":"small",single?"#fff":d.color,"",single?P[p].n:"",100);
      if(single){const e=markers[markers.length-1].el;if(e)e.querySelector(".pin").style.cssText+=`;background:#fff;border-color:${d.color};border-width:4px`}})});
    if(single)(SUBS[d.id]||[]).forEach(p=>{if(placed[d.id+p])return;placed[d.id+p]=1;addMk(p,"sub",d.color,"",P[p].n,100)});
  });
  applySel();
  requestAnimationFrame(declutter);
}
function midpoint(ll){
  let tot=0;const seg=[];for(let i=1;i<ll.length;i++){const s=map.distance(ll[i-1],ll[i]);seg.push(s);tot+=s}
  let h=tot/2;for(let i=0;i<seg.length;i++){if(h<=seg[i]){const t=seg[i]?h/seg[i]:0;return[ll[i][0]+(ll[i+1][0]-ll[i][0])*t,ll[i][1]+(ll[i+1][1]-ll[i][1])*t]}h-=seg[i]}
  return ll[ll.length-1];
}
// 标签避让：重叠时隐藏后来的（选中的优先）
function declutter(){
  const boxes=[];
  const list=markers.filter(x=>x.el&&x.el.querySelector(".lbl"));
  list.sort((a,b)=>(b.p===state.sel)-(a.p===state.sel)||(P[b.p].home?1:0)-(P[a.p].home?1:0));
  const pins=markers.filter(x=>x.el).map(x=>x.el.querySelector(".pin").getBoundingClientRect());
  list.forEach(x=>{const lb=x.el.querySelector(".lbl");lb.classList.remove("off");
    const r=lb.getBoundingClientRect();
    const hit=boxes.some(b=>!(r.right<b.left||r.left>b.right||r.bottom<b.top||r.top>b.bottom))||
              pins.some(b=>!(r.right<b.left+3||r.left>b.right-3||r.bottom<b.top+3||r.top>b.bottom-3));
    if(hit&&x.p!==state.sel){lb.classList.add("off");return}
    boxes.push({left:r.left-2,right:r.right+2,top:r.top-1,bottom:r.bottom+1});
  });
}
map.on("zoomend moveend",()=>requestAnimationFrame(declutter));

/* ---------- 点击/悬停：自己做命中测试，标记靠得近时选离手指最近的那个 ---------- */
function nearestMarker(cp,maxPx){
  let best=null,bd=Infinity;
  markers.forEach(x=>{const pt=map.latLngToContainerPoint(P[x.p].ll);const d=pt.distanceTo(cp);if(d<bd){bd=d;best=x}});
  return best&&bd<=maxPx?best:null;
}
function labelAt(clientX,clientY){
  return markers.find(x=>{const lb=x.el&&x.el.querySelector(".lbl:not(.off)");if(!lb)return false;const r=lb.getBoundingClientRect();
    return clientX>=r.left-2&&clientX<=r.right+2&&clientY>=r.top-2&&clientY<=r.bottom+2});
}
function nearestLeg(cp,maxPx){
  let best=null,bd=Infinity;
  legLines.forEach(x=>{const pts=x.ll.map(p=>map.latLngToContainerPoint(p));
    for(let i=1;i<pts.length;i++){const d=L.LineUtil.pointToSegmentDistance(cp,pts[i-1],pts[i]);if(d<bd){bd=d;best=x}}});
  return best&&bd<=maxPx?best:null;
}
const coarse=matchMedia("(pointer:coarse)").matches;
map.on("click",e=>{
  hideTip();
  const cp=e.containerPoint,oe=e.originalEvent;
  const mk=nearestMarker(cp,coarse?28:20)||(oe&&labelAt(oe.clientX,oe.clientY));
  if(mk){selectStop(mk.d,mk.p,true);return}
  const lg=nearestLeg(cp,coarse?14:9);
  if(lg){openLegPop(lg,e.latlng);return}
  map.closePopup();
});
const tip=document.getElementById("tip");
function showTip(cp,t){tip.textContent=t;tip.style.display="block";
  let x=cp.x+14,y=cp.y+14;const w=mapwrap.clientWidth;if(x+tip.offsetWidth>w-6)x=Math.max(6,w-tip.offsetWidth-6);tip.style.left=x+"px";tip.style.top=y+"px"}
function hideTip(){tip.style.display="none"}
let hoverRaf=0;
map.on("mousemove",e=>{if(coarse)return;cancelAnimationFrame(hoverRaf);hoverRaf=requestAnimationFrame(()=>{
  const mk=nearestMarker(e.containerPoint,20)||labelAt(e.originalEvent.clientX,e.originalEvent.clientY);
  if(mk){mapEl.style.cursor="pointer";showTip(e.containerPoint,P[mk.p].n);return}
  const lg=nearestLeg(e.containerPoint,9);
  if(lg){mapEl.style.cursor="pointer";const m=MODES[lg.lg.mode];showTip(e.containerPoint,`${m.ic} ${m.n} · ${shortN(lg.lg.from)} → ${shortN(lg.lg.to)} · ${lg.lg.dur}`);return}
  mapEl.style.cursor="";hideTip()})});
map.on("mouseout dragstart zoomstart",hideTip);

/* ---------- 弹窗（autoPan + 宽度随地图，保证不超出地图） ---------- */
function popOpts(){const w=mapwrap.clientWidth;return{maxWidth:Math.max(160,Math.min(270,w-70)),minWidth:Math.min(170,w-90),autoPan:true,keepInView:true,
  autoPanPaddingTopLeft:L.point(10,isNarrow()?12:56),autoPanPaddingBottomRight:L.point(10,24),closeButton:true,className:"pp"}}
function openStopPop(d,p){
  const pl=P[p];const items=visibleItems(d).filter(i=>!i.leg&&i.p===p);const it=items[0];
  const times=items.map(i=>i.t).join(" / ");
  const head=pl.sub?`<div style="margin-top:4px">属于「${P[pl.sub].n}」这一站（跟团行程）</div>`:(it&&it.h?`<div style="margin-top:4px">${it.h}</div>`:"");
  const html=`<h4>${pl.n}</h4><div class="t">${d.date} ${d.wk}${times?" · "+times:""}</div>${head}<div style="margin-top:6px"><a href="${gmPlace(pl)}" target="_blank" rel="noopener">在 Google Maps 打开 ↗</a></div>`;
  L.popup(popOpts()).setLatLng(pl.ll).setContent(html).openOn(map);
}
function openLegPop(x,at){
  const lg=x.lg,m=MODES[lg.mode],info=legInfo(lg);
  const km=info&&info.dist?` · 路线约 ${fmtDist(info.dist)}`:"";
  const html=`<h4>${m.ic} ${m.n}</h4><div class="t">${x.d.date} ${x.d.wk} · ${lg.dur}${km}</div><div style="margin-top:4px">${shortN(lg.from)} → ${shortN(lg.to)}</div>${lg.note?`<div class="t" style="margin-top:2px">${lg.note}</div>`:""}${info&&info.kind==="schematic"?`<div class="t">园内路线为示意</div>`:""}${NO_NAV.has(lg.to)?"":`<div style="margin-top:4px"><a href="${gmDir(lg.from,lg.to,lg.mode)}" target="_blank" rel="noopener">导航 ↗</a></div>`}`;
  highlightLeg(x);
  L.popup(popOpts()).setLatLng(at||midpoint(x.ll)).setContent(html).openOn(map);
}
let hlTimer=0;
function highlightLeg(x){
  legLines.forEach(o=>o.line.setStyle({opacity:o===x?1:(state.day?.35:.25)}));
  x.line.bringToFront();clearTimeout(hlTimer);
}
map.on("popupopen",()=>mapwrap.classList.add("popopen"));
map.on("popupclose",()=>{mapwrap.classList.remove("popopen");legLines.forEach(o=>{const schem=(legInfo(o.lg)||{}).kind==="schematic";o.line.setStyle({opacity:state.day?(schem?.6:1):.8})});
  document.querySelectorAll(".leg.sel").forEach(e=>e.classList.remove("sel"))});
const fmtDist=m=>m>=1000?(m/1000).toFixed(m>=10000?0:1)+" km":Math.round(m/10)*10+" m";

/* ---------- 视野 ---------- */
function fitLL(list,opt={}){
  if(!list.length)return;
  const b=L.latLngBounds(list);
  const pad=isNarrow()?[22,22]:[56,56];
  const o={paddingTopLeft:L.point(pad[0],pad[1]+(opt.top||0)),paddingBottomRight:L.point(pad[0],pad[1]),maxZoom:opt.maxZoom||17};
  flyView(b,o);
}
// flyTo 在起止视野几乎相同或地图尚无尺寸时会算出 NaN（Leaflet 已知问题），这时直接 setView
function flyView(b,o){
  const sz=map.getSize();
  if(!sz.x||!sz.y){map.fitBounds(b,Object.assign({animate:false},o));return}
  const z=Math.min(map.getBoundsZoom(b,false,o.paddingTopLeft.add(o.paddingBottomRight)),o.maxZoom);
  const off=o.paddingBottomRight.subtract(o.paddingTopLeft).divideBy(2);
  const c=map.unproject(map.project(b.getCenter(),z).add(off),z);
  const far=Math.abs(z-map.getZoom())>.01||map.latLngToContainerPoint(c).distanceTo(sz.divideBy(2))>2;
  if(!far){map.fire("moveend");return}
  try{map.flyTo(c,z,{duration:.55})}catch(e){map.setView(c,z,{animate:false})}
}
function flyPoint(ll,z){
  const sz=map.getSize();
  if(!sz.x||Math.abs(z-map.getZoom())<.01&&map.latLngToContainerPoint(ll).distanceTo(sz.divideBy(2))<2){map.setView(ll,z,{animate:false});map.fire("moveend");return}
  try{map.flyTo(ll,z,{duration:.5})}catch(e){map.setView(ll,z,{animate:false})}
}
function fitDay(){
  map.closePopup();
  if(!state.day){ // 总览：市区（蓝山团车线往西出画）
    const all=[];DAYS.forEach(d=>stopsOf(d).forEach(s=>{if(s.p!=="bluemtn")all.push(P[s.p].ll)}));all.push(P.airport.ll);
    fitLL(all,{maxZoom:14});return}
  const d=dayById(state.day);const all=[];
  visibleItems(d).forEach(i=>{if(i.leg)legPath(i).forEach(p=>all.push(p));else all.push(P[i.p].ll)});
  fitLL(all,{maxZoom:17,top:isNarrow()?20:30});
}
function toggleBig(){
  mapwrap.classList.toggle("big");const big=mapwrap.classList.contains("big");
  const b=document.querySelector(".ctl-exp");b.textContent=big?"⇡":"⇕";b.setAttribute("aria-label",big?"收起地图":"展开地图");
  setTimeout(()=>{map.invalidateSize();setMapH();},260);
}
function setMapH(){document.documentElement.style.setProperty("--mapHpx",mapwrap.offsetHeight+"px")}

/* ======================= Google Maps 链接（同原页面） ======================= */
const enc=encodeURIComponent;
const gmPlace=pl=>`https://www.google.com/maps/search/?api=1&query=${enc(pl.q||pl.ll.join(","))}`;
const gmDir=(a,b,mode)=>`https://www.google.com/maps/dir/?api=1&origin=${enc(P[a].q||P[a].ll.join(","))}&destination=${enc(P[b].q||P[b].ll.join(","))}&travelmode=${GMODE[mode]}`;
const shortN=id=>P[id].n.replace(/（.*?）/g,"").replace(/\s*·\s*89 Bay St/,"");
const qOf=id=>P[id].q||P[id].ll.join(",");
function gmSegments(d){
  const segs=[];let cur=null;
  legsOf(d).forEach(lg=>{
    if(lg.from===lg.to)return;
    if(lg.mode==="walk"){
      // 手机浏览器的 Google 地图链接每段最多 3 个中途点（= 5 个点）
      if(cur&&cur.mode==="walk"&&cur.stops[cur.stops.length-1]===lg.from&&cur.stops.length<5&&!(lg.from==="home"&&cur.stops.length>1)){cur.stops.push(lg.to)}
      else{cur={mode:"walk",stops:[lg.from,lg.to]};segs.push(cur)}
    }else{cur={mode:lg.mode,stops:[lg.from,lg.to],note:lg.note};segs.push(cur);cur=null}
  });
  return segs.map(sg=>{
    const o=sg.stops[0],dst=sg.stops[sg.stops.length-1],wp=sg.stops.slice(1,-1);
    let url=`https://www.google.com/maps/dir/?api=1&origin=${enc(qOf(o))}&destination=${enc(qOf(dst))}&travelmode=${GMODE[sg.mode]}`;
    if(wp.length)url+=`&waypoints=${wp.map(w=>enc(qOf(w))).join("%7C")}`;
    return {mode:sg.mode,stops:sg.stops,url};
  });
}
function gmBlock(d){
  const segs=gmSegments(d);
  let h=`<details class="gm" open><summary>🗺️ 在 Google 地图看真实路线 <span>可导航 · 实时班次 · ${segs.length} 段</span></summary><div class="gmlist">`;
  segs.forEach(sg=>{const m=MODES[sg.mode];
    const label=sg.stops.map(shortN).join(" → ");
    const tag=sg.mode==="coach"?"团车路线参考":sg.mode==="walk"?(sg.stops.length>2?"步行全程":"步行"):m.n;
    h+=`<a class="gmrow" href="${sg.url}" target="_blank" rel="noopener"><span class="gmi" style="border-color:${m.c}">${m.ic}</span><span class="gmt"><b>${tag}</b>${label}</span><span class="gmgo">↗</span></a>`});
  h+=`</div><div class="gmnote">按当天顺序排列，一段一个链接。步行段把沿途几个点串成一条路线；公交、火车、渡轮由 Google 按实时班次给方案。</div></details>`;
  return h;
}

/* ======================= 侧栏 ======================= */
const tabs=document.getElementById("tabs"),content=document.getElementById("content");
function renderTabs(){
  tabs.innerHTML="";
  const mk=(id,label,color)=>{const b=document.createElement("button");b.className="tab"+(state.day===id?" on":"");
    b.innerHTML=(color?`<span class="dot" style="background:${color}"></span>`:"")+label;b.onclick=()=>go(id);tabs.appendChild(b)};
  mk(null,"总览");DAYS.forEach(d=>mk(d.id,`${d.date} ${d.wk}`,d.color));
  const on=tabs.querySelector(".on");if(on)tabs.scrollLeft=on.offsetLeft-tabs.clientWidth/2+on.offsetWidth/2;
}
function renderLegend(){
  const lg=document.getElementById("legend");
  const sw=m=>`<svg width="26" height="8"><line x1="2" y1="4" x2="24" y2="4" stroke="${m.c}" stroke-width="3.5" stroke-dasharray="${m.dash}" stroke-linecap="round"/></svg>`;
  if(!state.day){lg.innerHTML=DAYS.map(d=>`<span><svg width="12" height="12"><circle cx="6" cy="6" r="5" fill="${d.color}"/></svg>${d.date}</span>`).join("");return}
  const used=new Set(legsOf(dayById(state.day)).map(l=>l.mode));
  lg.innerHTML=Object.entries(MODES).filter(([k])=>used.has(k)).map(([k,m])=>`<span>${sw(m)}${m.n}</span>`).join("");
}
function go(id,push=true){
  state.day=id;state.sel=null;map.closePopup();renderTabs();renderContent();render();renderLegend();fitDay();
  if(push){try{history.replaceState(null,"",id?"#"+id:"#overview")}catch(e){}}
  content.scrollTop=0;if(isNarrow())window.scrollTo({top:0});
}
function renderContent(){
  if(!state.day){renderOverview();return}
  const d=dayById(state.day);const num=numbering(d);
  let h=`<div class="dayhead"><div class="kicker"><span class="dot" style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${d.color}"></span>${d.date} ${d.wk}</div><h2>${d.title}</h2><div style="color:#3b3f45">${d.sum}</div><div class="chips">${d.chips.map(c=>`<span class="chip">${c}</span>`).join("")}</div></div>`;
  if(d.variants){h+=`<div class="seg" role="tablist" aria-label="${d.variants.label}">${d.variants.opts.map(o=>`<button data-v="${o[0]}" class="${state.variant[d.id]===o[0]?"on":""}">${o[1]}</button>`).join("")}</div>`}
  h+=gmBlock(d);
  if(loadErr)h+=`<div class="warn">真实路线数据没加载到（${loadErr.message}），地图上暂时显示近似折线。</div>`;
  (d.notes||[]).forEach(n=>h+=`<div class="note ${n[0]}">${n[1]}</div>`);
  h+=`<ol class="tl">`;
  visibleItems(d).forEach((it,idx)=>{
    if(it.leg){const m=MODES[it.mode],info=legInfo(it);
      const km=info&&info.dist&&info.kind!=="schematic"?`<span class="km">路线 ${fmtDist(info.dist)}</span>`:"";
      h+=`<li class="leg" data-i="${idx}"><div></div><div class="rail"><i style="border-left-color:${m.c};border-left-style:${it.mode==="walk"?"dotted":"solid"}"></i></div><div class="body"><span class="mode">${m.ic} ${m.n}</span><span>${it.dur}</span>${it.note?`<span>· ${it.note}</span>`:""}${km}${NO_NAV.has(it.to)?"":`<a class="nav" href="${gmDir(it.from,it.to,it.mode)}" target="_blank" rel="noopener">导航 ↗</a>`}${it.alt?`<span class="alt">替代：${it.alt}</span>`:""}</div></li>`;
    }else{const pl=P[it.p];
      const badge=pl.home?`<span class="badge" style="background:#1F2328">家</span>`:`<span class="badge" style="background:${it.extra?"#9AA0A6":d.color}">${num[it.p]}</span>`;
      h+=`<li class="stop" data-p="${it.p}"><div class="time">${it.t}</div>${badge}<div><h3>${it.h}${it.opt?'<span class="opt">可选</span>':""}</h3><div style="font-size:12px;color:#6B6F76">${pl.n}</div>${it.d?`<p>${it.d}</p>`:""}${it.tip?`<span class="tipline">${it.tip}</span>`:""}</div></li>`;
    }
  });
  h+=`</ol>`;
  const i=DAYS.indexOf(d);
  h+=`<div style="display:flex;justify-content:space-between;margin-top:16px">${i>0?`<a href="#" data-go="${DAYS[i-1].id}">← ${DAYS[i-1].date}</a>`:"<span></span>"}${i<DAYS.length-1?`<a href="#" data-go="${DAYS[i+1].id}">${DAYS[i+1].date} →</a>`:`<a href="#" data-go="">回总览</a>`}</div>`;
  content.innerHTML=h;
  content.querySelectorAll(".seg button").forEach(b=>b.onclick=()=>{state.variant[d.id]=b.dataset.v;state.sel=null;map.closePopup();renderContent();render();renderLegend();fitDay()});
  content.querySelectorAll(".stop").forEach(li=>li.onclick=()=>selectStop(d.id,li.dataset.p,false));
  const vis=visibleItems(d);
  content.querySelectorAll(".leg").forEach(li=>li.addEventListener("click",e=>{if(e.target.closest("a"))return;
    const lg=vis[+li.dataset.i];const x=legLines.find(o=>o.lg===lg);if(!x)return;
    content.querySelectorAll(".leg.sel,.stop.sel").forEach(e=>e.classList.remove("sel"));
    fitLL(x.ll,{maxZoom:17});
    map.once("moveend",()=>{openLegPop(x);li.classList.add("sel")});
    scrollMapIntoView();
  }));
  content.querySelectorAll("[data-go]").forEach(a=>a.onclick=e=>{e.preventDefault();go(a.dataset.go||null)});
}
function scrollMapIntoView(){ /* 手机上地图是 sticky 的，一直在视野里；桌面无需滚动 */ }
function applySel(){
  markers.forEach(x=>{const e=x.el&&x.el.querySelector(".mk");if(!e)return;e.classList.toggle("sel",x.p===state.sel);e.classList.toggle("dim",!!state.sel&&x.p!==state.sel)});
  markers.forEach(x=>x.m.setZIndexOffset(x.p===state.sel?1000:(P[x.p].home?500:200)));
}
function selectStop(dayId,p,fromMap){
  if(state.day!==dayId)go(dayId);
  state.sel=p;applySel();
  content.querySelectorAll(".stop").forEach(li=>li.classList.toggle("sel",li.dataset.p===p));
  content.querySelectorAll(".leg.sel").forEach(e=>e.classList.remove("sel"));
  const d=dayById(dayId);
  const z=Math.max(map.getZoom(),P[p].sub||p==="bluemtn"?14:16);
  map.closePopup();
  map.once("moveend",()=>{openStopPop(d,p);declutter()});
  flyPoint(P[p].ll,z);
  if(fromMap){const li=content.querySelector(`.stop[data-p="${p}"]`)||content.querySelector(`.stop[data-p="${P[p].sub}"]`);
    if(li){if(!isNarrow())li.scrollIntoView({block:"center",behavior:"smooth"});
      else{const top=li.getBoundingClientRect().top+window.scrollY-(tabs.offsetHeight+mapwrap.offsetHeight+10);window.scrollTo({top,behavior:"smooth"})}}}
}
function renderOverview(){
  let h=`<div class="note blue" style="margin-top:0">总体思路：<b>住在 Glebe，离市中心 3–5 km</b>。进城最省事是打车（约 15–20 分钟），公交 431/433 路沿 Glebe Point Rd 进城也很方便。城里景点之间 1 km 内步行，远一点用火车/轻轨/渡轮，回家累了直接打车。</div>`;
  if(loadErr)h+=`<div class="warn">真实路线数据没加载到（${loadErr.message}），地图上暂时显示近似折线。</div>`;
  DAYS.forEach(d=>h+=`<div class="daycard" data-go="${d.id}"><div class="bar" style="background:${d.color}"></div><div><div class="d">${d.date} ${d.wk}</div><h4>${d.title}</h4><p>${d.sum}</p></div></div>`);
  h+=`<div class="note green"><b>关于地图</b>：底图是 OpenStreetMap 街道地图，地图上的步行和打车路线是按真实街道算好的（步行可能和现场实际走法略有出入）；渡轮、火车、轻轨按 OSM 里的线路画，动物园园内路线是示意。要实时公交班次和导航，点每天页面顶部的“在 Google 地图看真实路线”，或每段旁边的“导航”。</div>`;
  h+=`<div class="sec"><h3>出发前要订的</h3><ul>
  <li><b>歌剧院普通话导览</b>（25 日上午）：官网选 “Mandarin Tour”，约 1 小时，只用中文讲解。有“导览 + 用餐”套餐可选（餐点需在当天 18:00 前兑换）。</li>
  <li><b>海德公园军营博物馆</b>（25 日）：免费，官网预约时段。</li>
  <li><b>塔龙加动物园</b>（26 日）：跟团就订团；自己去就在官网买门票（在线比门口便宜），渡轮刷卡即可，或买“渡轮 + 门票”套票。</li>
  <li><b>蓝山一日团</b>（27 日）：确认含 Scenic World 三种缆车、少徒步、中文导游、集合点在市中心。</li>
  </ul></div>`;
  h+=`<div class="sec"><h3>需要提前知道的</h3><ul>
  <li><b>交通刷卡</b>：火车、轻轨、公交、渡轮都可以直接用银行卡/手机钱包（Visa、Mastercard 等）刷，上车和下车都要刷，同一张卡不要混用。</li>
  <li><b>蓝花楹</b>：悉尼一般 10 月中开到 11 月下旬，你们去的时候是尾声。25 日在 Kirribilli、28 日在悉尼大学都顺路，不用专门跑。</li>
  <li><b>动物园缆车</b>：Sky Safari 已停运（新缆车预计 2027 年底），从码头上山靠 238 路公交。</li>
  <li><b>Happy Pho</b> 在 Kensington（UNSW 旁），网上信息显示周日休息，所以排在 28 日（周六）。</li>
  <li><b>日落</b>：11 月下旬约 19:40，看歌剧院亮灯可以待到 20:15 左右。</li>
  <li><b>没排进去的</b>：Kiama（南边海边小镇，看喷水洞）从 Central 坐火车单程要 2 小时以上，当天往返会很累；如果 28 日想换成海边一日游，可以用它替换休闲日。</li>
  </ul></div>`;
  h+=`<div class="sec"><h3>来源（出发前请再核对一次营业时间）</h3><ul class="src">
  <li><a href="https://www.sydneyoperahouse.com/tours/sydney-opera-house-tour" target="_blank" rel="noopener">Sydney Opera House – Tours（含普通话导览、步行与台阶说明）</a></li>
  <li><a href="https://www.infrastructure.nsw.gov.au/projects-nsw/new-sydney-fish-market/" target="_blank" rel="noopener">Infrastructure NSW – 新悉尼鱼市场 2026.1.19 开业</a></li>
  <li><a href="https://concreteplayground.com/global/food-drink/now-open-sydney-fish-market" target="_blank" rel="noopener">Concrete Playground – 鱼市场营业时间与地址</a></li>
  <li><a href="https://taronga.org.au/sydney-zoo/must-see/sky-safari" target="_blank" rel="noopener">Taronga – Sky Safari 停运与 238 路公交</a></li>
  <li><a href="https://www.taronga.org.au/sydney-zoo/plan/visitor-information/ticket-prices/" target="_blank" rel="noopener">Taronga – 门票价格</a></li>
  <li><a href="https://mhnsw.au/visit-us/hyde-park-barracks/plan-your-visit/" target="_blank" rel="noopener">Museums of History NSW – Hyde Park Barracks 开放时间</a></li>
  <li><a href="https://whatson.cityofsydney.nsw.gov.au/events/glebe-markets" target="_blank" rel="noopener">City of Sydney – Glebe Markets（周六 10:00–16:00）</a></li>
  <li><a href="https://www.northsydney.nsw.gov.au/news/article/250/reopening-mcdougall-street" target="_blank" rel="noopener">North Sydney Council – McDougall St 蓝花楹季</a></li>
  <li><a href="https://www.sydneycoastwalks.com.au/?p=15453" target="_blank" rel="noopener">Sydney Coast Walks – 海港大桥步行入口</a></li>
  <li><a href="https://www.onlinedining.com.au/venue/happy-pho" target="_blank" rel="noopener">Online Dining – Happy Pho 地址与营业时间</a></li>
  </ul><p class="src">地图数据 © OpenStreetMap contributors；步行/打车路线由 FOSSGIS 的 OSRM 服务在制作页面时算好存进页面，打开页面时不再依赖路线服务。地点坐标用 Nominatim 核对过。</p></div>`;
  content.innerHTML=h;
  content.querySelectorAll("[data-go]").forEach(c=>c.onclick=()=>go(c.dataset.go));
}

/* ======================= 启动 ======================= */
function setTabsH(){document.documentElement.style.setProperty("--tabsH",tabs.offsetHeight+"px")}
let lastW=window.innerWidth;
window.addEventListener("resize",()=>{setTabsH();map.invalidateSize();if(Math.abs(window.innerWidth-lastW)>2){lastW=window.innerWidth;fitDay()}});
const h0=(location.hash||"").slice(1);
go(dayById(h0)?h0:null,false);
setTabsH(); // 日期标签渲染之后再量高度，地图才会正好吸在日期栏下面
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(setTabsH);
window.addEventListener("hashchange",()=>{const h=(location.hash||"").slice(1);if((dayById(h)?h:null)!==state.day)go(dayById(h)?h:null,false)});
window.__app={map,state,ROUTES,GEO,go,selectStop,get markers(){return markers},get legLines(){return legLines}}; // 测试用
})();
