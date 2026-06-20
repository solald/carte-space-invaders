import json, sys, os
city_code, title, region, out_name, center = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
clat, clng = center.split(',')

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, 'world_invaders.json'), encoding='utf-8-sig'))
def f(x):
    x=(x or '').strip().replace(',','.')
    return float(x) if x not in ('','None') else None
rows=[]
for d in data:
    if d['city']!=city_code: continue
    rows.append({'id':d['id'],'lat':f(d.get('lat')),'lng':f(d.get('lng')),
        'status':(d.get('status') or '').strip(),
        'points':int(d['points']) if str(d.get('points','')).strip().isdigit() else None,
        'hint':(d.get('hint') or '').strip()})
rows=[r for r in rows if r['lat'] is not None and r['lng'] is not None]
rows.sort(key=lambda d:(len(d['id']),d['id']))
js=json.dumps(rows,ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Space Invaders de __TITLE__ — carte interactive</title>
<link rel="icon" type="image/svg+xml" href="invader.svg"/>
<meta name="theme-color" content="#3358d4"/>
<meta name="description" content="Carte interactive des Space Invaders de __TITLE__ : repère, flashe et construis ton itinéraire."/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="👾 Space Invaders de __TITLE__"/>
<meta property="og:description" content="Carte interactive : repère, flashe et construis ton itinéraire à plusieurs arrêts."/>
<meta property="og:image" content="https://solald.github.io/carte-space-invaders/og-image.png"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:image" content="https://solald.github.io/carte-space-invaders/og-image.png"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<style>
  :root{--bg:#eef1f5;--panel:#fff;--panel2:#f6f8fb;--txt:#1c2430;--muted:#5d6b7e;--accent:#3358d4;--found:#16a34a;}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--txt)}
  #map{position:absolute;inset:0;background:#eef1f5}
  .panel{position:absolute;z-index:1000;background:var(--panel);border:1px solid #d8dee7;border-radius:12px;box-shadow:0 6px 22px rgba(20,30,50,.12)}
  #header{top:12px;left:12px;right:12px;padding:10px 16px;display:flex;align-items:center;gap:8px 18px;flex-wrap:wrap}
  #header h1{font-size:16px;margin:0;font-weight:650}
  #header h1 span{color:var(--accent)}
  .stat{font-size:12px;color:var(--muted)}
  .stat b{color:var(--txt);font-variant-numeric:tabular-nums}
  .stat.found b{color:var(--found)}
  .progwrap{flex:1 1 160px;min-width:140px;height:8px;background:#e3e8ef;border-radius:6px;overflow:hidden}
  .progbar{height:100%;width:0;background:var(--found);transition:width .3s}
  #controls{top:74px;left:12px;width:248px;padding:12px 14px;font-size:13px}
  #controls h2{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);margin:0 0 8px;display:flex;align-items:center;gap:8px;cursor:pointer}
  #controls h2 .ccol{margin-left:auto;font-size:14px}
  #controls.collapsed h2{margin:0}
  #controls.collapsed > :not(h2){display:none}
  .row{display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;user-select:none}
  .row input{accent-color:var(--accent);width:15px;height:15px}
  .dot{width:11px;height:11px;border-radius:50%;flex:0 0 auto;border:1px solid rgba(0,0,0,.2)}
  .cnt{margin-left:auto;color:var(--muted);font-variant-numeric:tabular-nums}
  #search{margin-top:10px;width:100%;padding:7px 9px;border-radius:8px;border:1px solid #d8dee7;background:var(--panel2);color:var(--txt);font-size:13px}
  #search::placeholder{color:#9aa6b5}
  .sep{border-top:1px solid #e6eaf0;margin:10px 0}
  .toggle{display:flex;align-items:center;gap:8px;cursor:pointer}
  .toggle input{accent-color:var(--found);width:15px;height:15px}
  .btns{display:flex;gap:8px;margin-top:10px}
  .btn{flex:1;text-align:center;font-size:11px;padding:6px;border-radius:8px;border:1px solid #d8dee7;background:var(--panel2);color:var(--muted);cursor:pointer;text-decoration:none;display:block}
  .btn:hover{background:#eef2f7;color:var(--txt)}
  .hint-note{margin-top:10px;font-size:11px;color:var(--muted);line-height:1.45}
  .leaflet-popup-content-wrapper{background:#fff;color:var(--txt);border-radius:12px}
  .pop{min-width:200px;font-size:13px}
  .pop .id{font-size:16px;font-weight:700;margin-bottom:2px}
  .pop .badge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;font-weight:600;margin-bottom:8px}
  .pop .pts{font-weight:600}
  .pop .hint{color:var(--muted);font-style:italic;margin:6px 0}
  .pop a{color:var(--accent);text-decoration:none;display:inline-block;margin-top:6px;margin-right:12px;font-size:12px}
  .pop a:hover{text-decoration:underline}
  .flashbox{display:flex;align-items:center;gap:8px;margin-top:10px;padding:7px 9px;border:1px solid #d8dee7;border-radius:8px;background:var(--panel2);cursor:pointer;font-weight:600}
  .flashbox input{accent-color:var(--found);width:17px;height:17px}
  .flashbox.on{background:#e9f8ef;border-color:#bfe8cd;color:var(--found)}
  .routebtn{margin-top:8px;width:100%;padding:8px;border:1px solid var(--accent);border-radius:8px;background:var(--accent);color:#fff;font-weight:600;font-size:12.5px;cursor:pointer}
  .routebtn.on{background:#fff;color:var(--accent)}
  .marker-pin{width:15px;height:15px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1.5px rgba(0,0,0,.35);position:relative}
  .marker-pin.found{filter:grayscale(1);opacity:.55}
  .marker-pin.found::after{content:"\2713";position:absolute;inset:-2px;color:#fff;font-size:11px;font-weight:900;text-align:center;line-height:15px;text-shadow:0 0 2px rgba(0,0,0,.6)}
  .route-num{background:var(--accent);color:#fff;border:2px solid #fff;border-radius:50%;width:22px;height:22px;line-height:18px;text-align:center;font-size:12px;font-weight:700;box-shadow:0 1px 5px rgba(0,0,0,.45)}
  /* Panneau itinéraire */
  #routepanel{top:74px;right:12px;width:236px;padding:10px 12px;font-size:13px;max-height:calc(100vh - 92px);display:flex;flex-direction:column}
  #routehead{display:flex;align-items:center;gap:8px;cursor:pointer}
  #routehead .rt{font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--accent)}
  #routehead .rsum{margin-left:auto;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
  #routehead .rcol{color:var(--muted);font-size:14px;width:14px;text-align:center}
  #routelist{list-style:none;margin:8px 0 0;padding:0;overflow:auto;max-height:42vh}
  .ritem{display:flex;align-items:center;gap:8px;padding:5px 4px;border-radius:7px;cursor:pointer}
  .ritem:hover{background:var(--panel2)}
  .ritem .rnum{flex:0 0 auto;width:19px;height:19px;border-radius:50%;background:var(--accent);color:#fff;font-size:11px;font-weight:700;text-align:center;line-height:19px}
  .ritem .rid{font-weight:600;font-variant-numeric:tabular-nums}
  .ritem .rx{margin-left:auto;color:#b3bdca;font-weight:700;padding:0 4px}
  .ritem .rx:hover{color:var(--dest,#d23b30)}
  #r-warn{margin-top:8px;font-size:11px;color:#b26a00;background:#fff6e6;border:1px solid #ffe3ad;border-radius:7px;padding:6px 8px;display:none}
  #routepanel.collapsed #routelist,#routepanel.collapsed .btns,#routepanel.collapsed #r-warn{display:none}
  .credit{position:absolute;bottom:4px;right:8px;z-index:1000;font-size:10px;color:var(--muted);background:rgba(255,255,255,.75);padding:2px 6px;border-radius:6px}
  .credit a{color:var(--muted)}
  @media(max-width:640px){
    #controls{top:auto;bottom:12px;left:12px;right:12px;width:auto}
    #header h1{font-size:14px}
    #routepanel{top:78px;left:12px;right:12px;width:auto;max-height:44vh}
    #routelist{max-height:28vh}
  }
</style>
</head>
<body>
<div id="map"></div>
<div id="header" class="panel">
  <h1>👾 Space Invaders de <span>__TITLE__</span></h1>
  <div class="stat"><b id="s-total">0</b> mosaïques</div>
  <div class="stat found"><b id="s-found">0</b> trouvés</div>
  <div class="stat"><b id="s-left">0</b> restants</div>
  <div class="stat"><b id="s-pts">0</b> pts trouvés</div>
  <div class="progwrap"><div class="progbar" id="prog"></div></div>
</div>
<div id="controls" class="panel">
  <h2 id="controls-head">Filtres par statut <span class="ccol" id="c-collapse">▾</span></h2>
  <div id="filters"></div>
  <input id="search" placeholder="Chercher un code (ex : __EXAMPLE__)"/>
  <div class="sep"></div>
  <label class="toggle"><input type="checkbox" id="hidefound"> Masquer les trouvés</label>
  <div class="btns">
    <div class="btn" id="export">⬇️ Sauvegarder</div>
    <label class="btn" for="importfile">⬆️ Restaurer</label>
    <input type="file" id="importfile" accept=".json" style="display:none">
    <div class="btn" id="reset">♻️ Reset</div>
  </div>
  <div class="hint-note">Coche « Je l'ai flashé » dans la bulle d'un invader, ou « ➕ Ajouter à l'itinéraire » pour bâtir un parcours.</div>
</div>
<div id="routepanel" class="panel">
  <div id="routehead">
    <span class="rt">🚶 Itinéraire</span>
    <span class="rsum"><b id="r-count">0</b> arrêts · <span id="r-dist">0</span></span>
    <span class="rcol" id="r-collapse">▾</span>
  </div>
  <ol id="routelist"></ol>
  <div id="r-warn">Google Maps accepte ~10 arrêts : seuls les 10 premiers de l'ordre optimisé seront inclus dans le lien.</div>
  <div class="btns">
    <a class="btn" id="r-gmaps" href="#" target="_blank" rel="noopener" style="background:var(--accent);color:#fff;border-color:var(--accent)">🗺️ Google Maps</a>
    <div class="btn" id="r-clear">🧹 Vider</div>
  </div>
</div>
<div class="credit">Données : <a href="https://github.com/goguelnikov/SpaceInvaders" target="_blank">SpaceInvaders DB</a> · <a href="https://www.invader-spotter.art/" target="_blank">Invader-Spotter</a></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script>
const DATA = __DATA__;
const CITY = "__CITY__";
const STORE = "flashed_"+CITY;
const RSTORE = "route_"+CITY;
const COLORS={"OK":"#1fa463","a little damaged":"#cf9f0a","damaged":"#e08a16","very damaged":"#d2691e","destroyed":"#d23b30","hidden":"#6b7a8d"};
const LABELS={"OK":"Visible","a little damaged":"Légèrement endommagé","damaged":"Endommagé","very damaged":"Très endommagé","destroyed":"Détruit / disparu","hidden":"Caché"};
const ORDER=["OK","a little damaged","damaged","very damaged","destroyed","hidden"];
const FLASHABLE=s=>s!=="destroyed"&&s!=="hidden";
const BYID={}; DATA.forEach(d=>BYID[d.id]=d);

let flashed = new Set();
try{flashed = new Set(JSON.parse(localStorage.getItem(STORE)||"[]"));}catch(e){}
function save(){try{localStorage.setItem(STORE,JSON.stringify([...flashed]));}catch(e){}}

let route = [];
try{route = JSON.parse(localStorage.getItem(RSTORE)||"[]").filter(id=>BYID[id]);}catch(e){}
function saveRoute(){try{localStorage.setItem(RSTORE,JSON.stringify(route));}catch(e){}}

const map=L.map('map',{zoomControl:true}).setView([__CLAT__,__CLNG__],12);
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:20,subdomains:'abcd'}).addTo(map);

const cluster=L.markerClusterGroup({maxClusterRadius:50,spiderfyOnMaxZoom:true,chunkedLoading:true});
const routeLayer=L.layerGroup();
const markers=[];

function pinHtml(d){const c=COLORS[d.status]||'#888';return `<div class="marker-pin ${flashed.has(d.id)?'found':''}" style="background:${c}"></div>`;}
function setIcon(m){m.setIcon(L.divIcon({className:'',html:pinHtml(m._inv),iconSize:[15,15],iconAnchor:[7,7]}));}

function popupHtml(d){
  const c=COLORS[d.status]||'#888';
  const pin=`https://www.google.com/maps/search/?api=1&query=${d.lat},${d.lng}`;
  const sv=`https://www.google.com/maps?q=&layer=c&cbll=${d.lat},${d.lng}`;
  const img=`https://www.google.com/search?tbm=isch&q=${encodeURIComponent('Invader '+d.id)}`;
  const on=flashed.has(d.id);
  const inr=route.includes(d.id);
  return `<div class="pop">
    <div class="id">${d.id}</div>
    <span class="badge" style="background:${c}22;color:${c};border:1px solid ${c}66">${LABELS[d.status]||d.status}</span>
    <div class="pts">${d.points!=null?d.points+' points':'points n.c.'}</div>
    ${d.hint?`<div class="hint">“${d.hint}”</div>`:''}
    <a href="${pin}" target="_blank">📍 Voir sur Maps</a>
    <a href="${img}" target="_blank">🖼️ Photo</a>
    <a href="${sv}" target="_blank">📷 Street View</a>
    <label class="flashbox ${on?'on':''}"><input type="checkbox" ${on?'checked':''} onchange="toggleFlash('${d.id}',this.checked)"> ${on?'Flashé ✓':"Je l'ai flashé"}</label>
    <button class="routebtn ${inr?'on':''}" onclick="toggleRoute('${d.id}')">${inr?"✓ Dans l'itinéraire — retirer":"➕ Ajouter à l'itinéraire"}</button>
  </div>`;
}

function refreshPopup(id){const m=markers.find(x=>x._inv.id===id);if(m&&m.isPopupOpen())m.setPopupContent(popupHtml(m._inv));}

window.toggleFlash=function(id,val){
  if(val)flashed.add(id);else flashed.delete(id);
  save();
  const m=markers.find(x=>x._inv.id===id); if(m)setIcon(m);
  updateStats();
  if(document.getElementById('hidefound').checked)refresh();
  refreshPopup(id);
};

window.toggleRoute=function(id){
  const i=route.indexOf(id);
  if(i>=0)route.splice(i,1);else route.push(id);
  saveRoute();renderRoute();refreshPopup(id);
};
window.removeRoute=function(id){
  const i=route.indexOf(id);
  if(i>=0){route.splice(i,1);saveRoute();renderRoute();refreshPopup(id);}
};

DATA.forEach(d=>{
  const m=L.marker([d.lat,d.lng]);
  m._inv=d; setIcon(m);
  m.bindPopup(()=>popupHtml(d));
  m.bindTooltip(d.id,{direction:'top',offset:[0,-8]});
  markers.push(m);
});

const counts={};
DATA.forEach(d=>counts[d.status]=(counts[d.status]||0)+1);
const fc=document.getElementById('filters');
ORDER.filter(s=>counts[s]).forEach(s=>{
  const lab=document.createElement('label');lab.className='row';
  lab.innerHTML=`<input type="checkbox" data-st="${s}" checked><span class="dot" style="background:${COLORS[s]}"></span>${LABELS[s]}<span class="cnt">${counts[s]}</span>`;
  fc.appendChild(lab);
});

function refresh(){
  const active={};
  document.querySelectorAll('#filters input[data-st]').forEach(cb=>active[cb.dataset.st]=cb.checked);
  const q=(document.getElementById('search').value||'').trim().toUpperCase();
  const hf=document.getElementById('hidefound').checked;
  cluster.clearLayers();
  const sel=[];
  markers.forEach(m=>{const d=m._inv;
    if(active[d.status]===false)return;
    if(q&&!d.id.toUpperCase().includes(q))return;
    if(hf&&flashed.has(d.id))return;
    sel.push(m);});
  cluster.addLayers(sel);
}

function updateStats(){
  const flashableTotal=DATA.filter(d=>FLASHABLE(d.status)).length;
  let foundCount=0,foundPts=0;
  DATA.forEach(d=>{if(flashed.has(d.id)){foundCount++;foundPts+=d.points||0;}});
  const left=Math.max(0,flashableTotal-DATA.filter(d=>FLASHABLE(d.status)&&flashed.has(d.id)).length);
  document.getElementById('s-total').textContent=DATA.length;
  document.getElementById('s-found').textContent=foundCount;
  document.getElementById('s-left').textContent=left;
  document.getElementById('s-pts').textContent=foundPts.toLocaleString('fr-FR');
  document.getElementById('prog').style.width=(flashableTotal?100*(flashableTotal-left)/flashableTotal:0)+'%';
}

/* ---------- Itinéraire ---------- */
function hav(a,b){
  const R=6371000,t=Math.PI/180;
  const dLat=(b.lat-a.lat)*t,dLng=(b.lng-a.lng)*t,la1=a.lat*t,la2=b.lat*t;
  const x=Math.sin(dLat/2)**2+Math.cos(la1)*Math.cos(la2)*Math.sin(dLng/2)**2;
  return 2*R*Math.asin(Math.sqrt(x));
}
function pathLen(o){let s=0;for(let i=0;i<o.length-1;i++)s+=hav(o[i],o[i+1]);return s;}
function nearestNeighbor(pts,start){
  const n=pts.length,used=new Array(n).fill(false),o=[];
  let cur=start;used[cur]=true;o.push(pts[cur]);
  for(let k=1;k<n;k++){let best=-1,bd=Infinity;
    for(let j=0;j<n;j++)if(!used[j]){const d=hav(pts[cur],pts[j]);if(d<bd){bd=d;best=j;}}
    used[best]=true;o.push(pts[best]);cur=best;}
  return o;
}
function twoOpt(o){
  let improved=true,len=pathLen(o);
  while(improved){improved=false;
    for(let i=0;i<o.length-1;i++)for(let k=i+1;k<o.length;k++){
      const cand=o.slice(0,i).concat(o.slice(i,k+1).reverse(),o.slice(k+1));
      const cl=pathLen(cand);
      if(cl+1e-6<len){o=cand;len=cl;improved=true;}
    }}
  return o;
}
function optimize(pts){
  const n=pts.length;
  if(n<=2)return pts.slice();
  let best=null,bd=Infinity;
  const starts=n<=10?pts.map((_,i)=>i):[0];
  for(const s of starts){
    let o=nearestNeighbor(pts,s);
    if(n<=40)o=twoOpt(o);
    const d=pathLen(o);
    if(d<bd){bd=d;best=o;}
  }
  return best;
}
function fmtDist(m){return m<1000?Math.round(m)+' m':(m/1000).toFixed(1).replace('.',',')+' km';}
function gmapsUrl(o){
  const stops=o.slice(0,10).map(d=>d.lat+','+d.lng);
  const dest=encodeURIComponent(stops[stops.length-1]);
  const wpts=stops.slice(0,-1).map(encodeURIComponent).join('%7C');
  let u='https://www.google.com/maps/dir/?api=1&travelmode=walking&destination='+dest;
  if(wpts)u+='&waypoints='+wpts;
  return u;
}
function focusInvader(id){
  const m=markers.find(x=>x._inv.id===id);if(!m)return;
  if(cluster.zoomToShowLayer)cluster.zoomToShowLayer(m,()=>m.openPopup());
  else{map.setView([BYID[id].lat,BYID[id].lng],17);m.openPopup();}
}
function renderRoute(){
  const panel=document.getElementById('routepanel');
  routeLayer.clearLayers();
  if(route.length===0){panel.style.display='none';return;}
  panel.style.display='';
  const pts=route.map(id=>BYID[id]).filter(Boolean);
  const ordered=optimize(pts);
  const ol=document.getElementById('routelist');ol.innerHTML='';
  ordered.forEach((d,i)=>{
    const li=document.createElement('li');li.className='ritem';
    li.innerHTML=`<span class="rnum">${i+1}</span><span class="dot" style="background:${COLORS[d.status]||'#888'}"></span><span class="rid">${d.id}</span><span class="rx" title="Retirer">✕</span>`;
    li.addEventListener('click',()=>focusInvader(d.id));
    li.querySelector('.rx').addEventListener('click',e=>{e.stopPropagation();removeRoute(d.id);});
    ol.appendChild(li);
  });
  document.getElementById('r-count').textContent=route.length;
  document.getElementById('r-dist').textContent='~'+fmtDist(pathLen(ordered));
  document.getElementById('r-warn').style.display=route.length>10?'block':'none';
  document.getElementById('r-gmaps').href=gmapsUrl(ordered);
  if(ordered.length>=2)
    L.polyline(ordered.map(d=>[d.lat,d.lng]),{color:'#3358d4',weight:4,opacity:.75,dashArray:'1,9',lineCap:'round'}).addTo(routeLayer);
  ordered.forEach((d,i)=>{
    L.marker([d.lat,d.lng],{icon:L.divIcon({className:'',html:`<div class="route-num">${i+1}</div>`,iconSize:[22,22],iconAnchor:[11,11]}),zIndexOffset:1000,interactive:false}).addTo(routeLayer);
  });
}

document.querySelectorAll('#filters input[data-st]').forEach(cb=>cb.addEventListener('change',refresh));
document.getElementById('search').addEventListener('input',refresh);
document.getElementById('hidefound').addEventListener('change',refresh);
document.getElementById('reset').addEventListener('click',()=>{
  if(confirm('Effacer tous les invaders cochés ?')){flashed=new Set();save();markers.forEach(setIcon);updateStats();refresh();}
});
document.getElementById('export').addEventListener('click',()=>{
  const blob=new Blob([JSON.stringify([...flashed])],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='invaders-flashes-'+CITY+'.json';a.click();
});
document.getElementById('importfile').addEventListener('change',e=>{
  const f=e.target.files[0];if(!f)return;const r=new FileReader();
  r.onload=()=>{try{flashed=new Set(JSON.parse(r.result));save();markers.forEach(setIcon);updateStats();refresh();alert('Restauré : '+flashed.size+' invaders.');}catch(x){alert('Fichier invalide.');}};
  r.readAsText(f);
});
document.getElementById('r-clear').addEventListener('click',()=>{route=[];saveRoute();renderRoute();markers.forEach(m=>refreshPopup(m._inv.id));});
document.getElementById('routehead').addEventListener('click',()=>{
  const p=document.getElementById('routepanel');p.classList.toggle('collapsed');
  document.getElementById('r-collapse').textContent=p.classList.contains('collapsed')?'▸':'▾';
});
document.getElementById('controls-head').addEventListener('click',()=>{
  const p=document.getElementById('controls');p.classList.toggle('collapsed');
  document.getElementById('c-collapse').textContent=p.classList.contains('collapsed')?'▸':'▾';
});
if(window.matchMedia('(max-width:640px)').matches){
  document.getElementById('controls').classList.add('collapsed');
  document.getElementById('c-collapse').textContent='▸';
}

map.addLayer(cluster);
routeLayer.addTo(map);
updateStats();refresh();renderRoute();
map.fitBounds(L.featureGroup(markers).getBounds().pad(0.03));
</script>
</body>
</html>'''

example = rows[0]['id'] if rows else 'PA_100'
html=(html.replace('__TITLE__',title).replace('__REGION__',region).replace('__CITY__',city_code)
          .replace('__EXAMPLE__',example).replace('__CLAT__',clat).replace('__CLNG__',clng)
          .replace('__DATA__',js))
open(out_name,'w',encoding='utf-8').write(html)
print('written',out_name,len(rows),'invaders',len(html),'bytes')
