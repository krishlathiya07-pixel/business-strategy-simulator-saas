"""
Business Strategy Simulation — FastAPI Dashboard
Level 4: /dashboard endpoint with live charts, competitor comparison, history replay.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server.environment import BusinessStrategyEnv, INDUSTRIES

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Business Simulator")

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared simulation state ───────────────────────────────────────────────────
env = BusinessStrategyEnv(task="grow_market_share", seed=42)
revenue_history: list = []
profit_history:  list = []
share_history:   list = []
news_feed:       list = []

# Seed initial chart point
_s = env.state()
revenue_history.append(round(_s.get("revenue", 0), 2))
profit_history.append(round(_s.get("profit",  0), 2))
share_history.append(round(_s.get("market_share", 0) * 100, 2))


# ── Request bodies ────────────────────────────────────────────────────────────
class StepBody(BaseModel):
    action: str   = "expand_market"
    amount: float = 5000.0

class ResetBody(BaseModel):
    task: str = "grow_market_share"
    seed: int = 42


# ── Helpers ───────────────────────────────────────────────────────────────────
def _record(state: dict):
    revenue_history.append(round(state.get("revenue", 0), 2))
    profit_history.append(round(state.get("profit",  0), 2))
    share_history.append(round(state.get("market_share", 0) * 100, 2))
    news = state.get("news")
    if news:
        news_feed.insert(0, {"q": state.get("quarter", 0), "text": news})
    if len(news_feed) > 20:
        news_feed.pop()

def _with_charts(state: dict) -> dict:
    return {**state,
            "chart_revenue": revenue_history,
            "chart_profit":  profit_history,
            "chart_share":   share_history,
            "news_feed":     news_feed}


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    with open("server/tamplates/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
def api_state():
    return _with_charts(env.state())


@app.post("/api/step")
def api_step(body: StepBody):
    state = env.step(body.action, body.amount)
    _record(state)
    return _with_charts(state)


@app.post("/api/reset")
def api_reset(body: ResetBody):
    global env, revenue_history, profit_history, share_history, news_feed
    revenue_history, profit_history, share_history, news_feed = [], [], [], []
    env   = BusinessStrategyEnv(task=body.task, seed=body.seed)
    state = env.state()
    _record(state)
    return _with_charts(state)


@app.get("/api/history")
def api_history():
    return {"history": env.history}


@app.get("/api/industries")
def api_industries():
    return INDUSTRIES


# ── Dashboard HTML ────────────────────────────────────────────────────────────

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Business Simulator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {
    --bg:#080b0f; --panel:#0d1117; --border:#1a2535;
    --green:#00e676; --green-dim:#00664433; --red:#ff3d5a;
    --amber:#ffab00; --blue:#29b6f6; --purple:#ce93d8;
    --txt:#c9d1d9; --txt-dim:#586069;
    --mono:'Share Tech Mono',monospace; --sans:'Rajdhani',sans-serif;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--txt);font-family:var(--mono);font-size:13px;min-height:100vh;overflow-x:hidden}
  body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,230,118,.015) 2px,rgba(0,230,118,.015) 4px);pointer-events:none;z-index:9999}
  #topbar{display:flex;align-items:center;justify-content:space-between;padding:10px 18px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
  #topbar .logo{font-family:var(--sans);font-size:20px;font-weight:700;color:var(--green);letter-spacing:3px;text-transform:uppercase}
  #topbar .logo span{color:var(--txt-dim)}
  #clock{color:var(--amber);letter-spacing:2px}
  #news-ticker{flex:1;margin:0 24px;overflow:hidden;white-space:nowrap;color:var(--txt-dim);font-size:11px}
  #news-ticker-inner{display:inline-block;animation:ticker 30s linear infinite}
  @keyframes ticker{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}
  #main{display:grid;grid-template-columns:240px 1fr;gap:0;height:calc(100vh - 45px)}
  #sidebar{background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow-y:auto;padding:12px 10px;gap:10px}
  .section-label{font-family:var(--sans);font-size:10px;font-weight:700;color:var(--txt-dim);letter-spacing:3px;text-transform:uppercase;padding:4px 4px 2px;border-bottom:1px solid var(--border);margin-bottom:4px}
  .stat{display:flex;justify-content:space-between;padding:3px 4px}
  .stat .lbl{color:var(--txt-dim)} .stat .val{font-weight:bold}
  .pos{color:var(--green)} .neg{color:var(--red)} .neu{color:var(--amber)} .info{color:var(--blue)}
  .comp-chip{display:flex;align-items:center;gap:6px;background:#0a1220;border:1px solid var(--border);border-radius:4px;padding:5px 8px;margin-bottom:4px;font-size:11px}
  .comp-chip .bar-outer{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden}
  .comp-chip .bar-inner{height:100%;border-radius:3px}
  .action-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px}
  .btn-action{background:#0d1a12;border:1px solid #1a3a20;color:var(--green);font-family:var(--mono);font-size:10px;padding:6px 4px;cursor:pointer;border-radius:3px;text-align:center;transition:background .15s,border-color .15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .btn-action:hover{background:#163020;border-color:var(--green)}
  .btn-action.danger{background:#1a0d10;border-color:#3a1a20;color:var(--red)}
  .btn-action.danger:hover{background:#2a1015;border-color:var(--red)}
  .btn-action.neutral{background:#1a140d;border-color:#3a2a10;color:var(--amber)}
  .btn-action.neutral:hover{background:#2a1e10;border-color:var(--amber)}
  #amount-row{display:flex;gap:6px;align-items:center}
  #amount-row label{color:var(--txt-dim);font-size:11px}
  #amount-input{flex:1;background:#0a1220;border:1px solid var(--border);color:var(--txt);font-family:var(--mono);font-size:12px;padding:5px 8px;border-radius:3px;outline:none}
  #amount-input:focus{border-color:var(--green)}
  .btn-reset{width:100%;background:transparent;border:1px solid #2a1a30;color:var(--purple);font-family:var(--mono);font-size:11px;padding:7px;cursor:pointer;border-radius:3px;transition:background .15s}
  .btn-reset:hover{background:#1a0d20}
  select{width:100%;background:#0a1220;border:1px solid var(--border);color:var(--txt);font-family:var(--mono);font-size:12px;padding:5px 8px;border-radius:3px;outline:none;cursor:pointer;margin-bottom:4px}
  select:focus{border-color:var(--green)}
  #content{display:grid;grid-template-rows:1fr 1fr;grid-template-columns:1fr 1fr;gap:0;overflow:hidden}
  .chart-panel{border-right:1px solid var(--border);border-bottom:1px solid var(--border);padding:10px 14px;display:flex;flex-direction:column;overflow:hidden}
  .chart-panel:nth-child(2),.chart-panel:nth-child(4){border-right:none}
  .panel-title{font-family:var(--sans);font-weight:700;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--txt-dim);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}
  .panel-badge{font-size:10px;font-family:var(--mono);background:var(--green-dim);color:var(--green);padding:1px 6px;border-radius:10px;font-weight:normal}
  canvas{flex:1;min-height:0}
  #history-wrap{overflow-y:auto;flex:1;margin-top:4px}
  table{width:100%;border-collapse:collapse;font-size:11px}
  th{text-align:left;padding:4px 6px;color:var(--txt-dim);border-bottom:1px solid var(--border);font-family:var(--sans);font-size:10px;letter-spacing:1px;text-transform:uppercase;position:sticky;top:0;background:var(--panel)}
  td{padding:3px 6px;border-bottom:1px solid #0f1a24}
  tr:hover td{background:#0d1520} tr.latest td{background:#0d1a12}
  @keyframes flash-green{0%{background:rgba(0,230,118,.18)}100%{background:transparent}}
  .flash{animation:flash-green .6s ease-out}
  #gameover{display:none;position:fixed;inset:0;z-index:200;background:rgba(8,11,15,.92);align-items:center;justify-content:center;flex-direction:column;gap:16px}
  #gameover.show{display:flex}
  #gameover .msg{font-family:var(--sans);font-size:36px;font-weight:700;color:var(--red);letter-spacing:4px;text-transform:uppercase;text-align:center}
  #gameover .sub{color:var(--txt-dim);font-size:13px}
  #gameover button{background:transparent;border:1px solid var(--purple);color:var(--purple);font-family:var(--mono);font-size:14px;padding:10px 30px;cursor:pointer;border-radius:3px;transition:background .15s}
  #gameover button:hover{background:#1a0d20}
  .industry-pill{display:inline-block;background:#1a1a2e;border:1px solid #2a2a4e;color:var(--purple);border-radius:10px;padding:2px 8px;font-size:10px}
</style>
</head>
<body>

<div id="topbar">
  <div class="logo">Biz<span>Sim</span> Terminal</div>
  <div id="news-ticker"><div id="news-ticker-inner">Loading market data…</div></div>
  <div id="clock">00:00:00</div>
</div>

<div id="gameover">
  <div class="msg" id="gameover-msg">GAME OVER</div>
  <div class="sub" id="gameover-sub"></div>
  <button onclick="doReset()">↩ NEW GAME</button>
</div>

<div id="main">
  <div id="sidebar">
    <div class="section-label">Company</div>
    <div id="industry-row" style="margin-bottom:4px"></div>
    <div class="stat"><span class="lbl">Revenue</span>     <span class="val pos"  id="s-rev">—</span></div>
    <div class="stat"><span class="lbl">Costs</span>       <span class="val neg"  id="s-costs">—</span></div>
    <div class="stat"><span class="lbl">Profit</span>      <span class="val"      id="s-profit">—</span></div>
    <div class="stat"><span class="lbl">Mkt Share</span>   <span class="val info" id="s-share">—</span></div>
    <div class="stat"><span class="lbl">Employees</span>   <span class="val neu"  id="s-emp">—</span></div>
    <div class="stat"><span class="lbl">Satisfaction</span><span class="val pos"  id="s-sat">—</span></div>
    <div class="stat"><span class="lbl">Quality</span>     <span class="val pos"  id="s-qual">—</span></div>
    <div class="stat"><span class="lbl">Quarter</span>     <span class="val"      id="s-q">—</span></div>
    <div class="stat"><span class="lbl">Rank</span>        <span class="val"      id="s-rank">—</span></div>
    <div class="stat"><span class="lbl">Reward</span>      <span class="val"      id="s-reward">—</span></div>
    <div class="section-label" style="margin-top:6px">Competitors</div>
    <div id="comp-list"></div>
    <div class="section-label" style="margin-top:6px">Actions</div>
    <div id="amount-row"><label>$</label><input id="amount-input" type="number" value="5000" min="500" step="500"></div>
    <div class="action-grid">
      <button class="btn-action"         onclick="doStep('increase_marketing')">📣 Mkt ↑</button>
      <button class="btn-action"         onclick="doStep('expand_market')">🌍 Expand</button>
      <button class="btn-action"         onclick="doStep('hire_employees')">👷 Hire</button>
      <button class="btn-action"         onclick="doStep('invest_in_rd')">🔬 R&amp;D</button>
      <button class="btn-action"         onclick="doStep('launch_product')">🚀 Launch</button>
      <button class="btn-action neutral" onclick="doStep('raise_prices')">💰 Raise $</button>
      <button class="btn-action neutral" onclick="doStep('lower_prices')">🏷 Lower $</button>
      <button class="btn-action neutral" onclick="doStep('cut_costs')">✂️ Costs</button>
      <button class="btn-action danger"  onclick="doStep('layoff_employees')">📉 Layoff</button>
      <button class="btn-action danger"  onclick="doStep('decrease_marketing')">📣 Mkt ↓</button>
    </div>
    <div class="section-label" style="margin-top:6px">New Game</div>
    <select id="task-select">
      <option value="survive">survive (4 Q)</option>
      <option value="grow_market_share" selected>grow_market_share (8 Q)</option>
      <option value="scale_profitably">scale_profitably (12 Q)</option>
    </select>
    <button class="btn-reset" onclick="doReset()">⟳ Reset Simulation</button>
  </div>

  <div id="content">
    <div class="chart-panel">
      <div class="panel-title">📈 Revenue &amp; Profit <span class="panel-badge" id="badge-rev">LIVE</span></div>
      <canvas id="chartRevenue"></canvas>
    </div>
    <div class="chart-panel">
      <div class="panel-title">🥧 Market Share <span class="panel-badge" id="badge-share">LIVE</span></div>
      <canvas id="chartPie"></canvas>
    </div>
    <div class="chart-panel">
      <div class="panel-title">⚔️ Competitor Comparison <span class="panel-badge" id="badge-comp">LIVE</span></div>
      <canvas id="chartBar"></canvas>
    </div>
    <div class="chart-panel" style="flex-direction:column;overflow:hidden">
      <div class="panel-title">📋 History Replay</div>
      <div id="history-wrap">
        <table>
          <thead><tr><th>Q</th><th>Action</th><th>Profit</th><th>Share</th><th>Rank</th><th>Event</th></tr></thead>
          <tbody id="history-body"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
Chart.defaults.color='#586069';Chart.defaults.borderColor='#1a2535';
Chart.defaults.font.family="'Share Tech Mono',monospace";Chart.defaults.font.size=11;
const GREEN='#00e676',RED='#ff3d5a',AMBER='#ffab00',BLUE='#29b6f6',DIM='#586069';

const chartRev=new Chart(document.getElementById('chartRevenue'),{
  type:'line',data:{labels:[],datasets:[
    {label:'Revenue',data:[],borderColor:GREEN,backgroundColor:'rgba(0,230,118,.08)',fill:true,tension:0.35,pointRadius:3,borderWidth:2},
    {label:'Profit', data:[],borderColor:AMBER,backgroundColor:'rgba(255,171,0,.06)', fill:true,tension:0.35,pointRadius:3,borderWidth:2,borderDash:[4,3]}
  ]},options:{responsive:true,maintainAspectRatio:false,animation:{duration:300},
    plugins:{legend:{labels:{boxWidth:10,padding:12}}},
    scales:{x:{grid:{color:'#111c2a'},ticks:{maxTicksLimit:8}},
            y:{grid:{color:'#111c2a'},ticks:{callback:v=>v>=1000?'$'+(v/1000).toFixed(0)+'k':'$'+v}}}}
});

const chartPie=new Chart(document.getElementById('chartPie'),{
  type:'doughnut',data:{labels:['You','RivalCorp','MegaCo','Other'],datasets:[{
    data:[10,25,40,25],backgroundColor:[GREEN,RED,BLUE,DIM],borderColor:'#080b0f',borderWidth:3,hoverOffset:8
  }]},options:{responsive:true,maintainAspectRatio:false,animation:{duration:400},cutout:'62%',
    plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:10}},
             tooltip:{callbacks:{label:ctx=>' '+ctx.label+': '+ctx.parsed.toFixed(1)+'%'}}}}
});

const chartBar=new Chart(document.getElementById('chartBar'),{
  type:'bar',data:{labels:['Market Share %','Satisfaction×100','Quality×100'],datasets:[
    {label:'You',      data:[10,70,65],backgroundColor:'rgba(0,230,118,.65)',borderColor:GREEN,borderWidth:1},
    {label:'RivalCorp',data:[25,60,60],backgroundColor:'rgba(255,61,90,.55)', borderColor:RED,  borderWidth:1},
    {label:'MegaCo',   data:[40,75,70],backgroundColor:'rgba(41,182,246,.55)',borderColor:BLUE, borderWidth:1}
  ]},options:{responsive:true,maintainAspectRatio:false,animation:{duration:300},
    plugins:{legend:{labels:{boxWidth:10,padding:10}}},
    scales:{x:{grid:{color:'#111c2a'}},y:{grid:{color:'#111c2a'},min:0,max:100}}}
});

function fmt$(n){return'$'+Number(n).toLocaleString('en-US',{maximumFractionDigits:0})}
function fmtPct(n){return(n*100).toFixed(1)+'%'}
function fmtN(v){return Math.round((v||0)*100)}
function rankStr(r){return['🥇','🥈','🥉'][Math.min(r-1,2)]||'#'+r}
let env_history=[];

function updateUI(d){
  const prof=d.profit||0;
  const setV=(id,v,cls)=>{const el=document.getElementById(id);el.textContent=v;el.className='val '+(cls||'')};
  setV('s-rev',   fmt$(d.revenue),                  'pos');
  setV('s-costs', fmt$(d.costs),                    'neg');
  setV('s-profit',fmt$(prof),                       prof>=0?'pos':'neg');
  setV('s-share', fmtPct(d.market_share||0),        'info');
  setV('s-emp',   d.employees,                      'neu');
  setV('s-sat',   fmtPct(d.customer_satisfaction||0),'pos');
  setV('s-qual',  fmtPct(d.product_quality||0),     'pos');
  setV('s-q',     'Q'+(d.quarter||0)+' / '+(d.max_quarters||0));
  setV('s-rank',  rankStr(d.market_rank||3));
  setV('s-reward',(d.reward||0).toFixed(3),         d.reward>=0.7?'pos':'neu');

  document.getElementById('industry-row').innerHTML=
    '<span class="industry-pill">🏭 '+(d.industry||'unknown').replace('_',' ')+'</span>';

  const comps=d.competitors||[];
  document.getElementById('comp-list').innerHTML=comps.map(c=>{
    const pct=Math.round((c.market_share||0)*100);
    const col=c.name==='RivalCorp'?'#ff3d5a':'#29b6f6';
    return'<div class="comp-chip"><span>'+c.emoji+' '+c.name+'</span>'+
      '<div class="bar-outer"><div class="bar-inner" style="width:'+Math.min(pct*1.5,100)+'%;background:'+col+'"></div></div>'+
      '<span style="color:'+col+';min-width:30px;text-align:right">'+pct+'%</span></div>';
  }).join('');

  if(d.chart_revenue&&d.chart_profit){
    chartRev.data.labels=d.chart_revenue.map((_,i)=>'Q'+i);
    chartRev.data.datasets[0].data=d.chart_revenue;
    chartRev.data.datasets[1].data=d.chart_profit;
    chartRev.update();
  }
  const you=(d.market_share||0)*100,c0=(comps[0]?.market_share||0)*100,c1=(comps[1]?.market_share||0)*100;
  chartPie.data.datasets[0].data=[you.toFixed(1),c0.toFixed(1),c1.toFixed(1),Math.max(0,100-you-c0-c1).toFixed(1)];
  chartPie.update();
  chartBar.data.datasets[0].data=[you.toFixed(1),fmtN(d.customer_satisfaction),fmtN(d.product_quality)];
  chartBar.data.datasets[1].data=[c0.toFixed(1),60,60];
  chartBar.data.datasets[2].data=[c1.toFixed(1),75,70];
  chartBar.update();

  document.getElementById('history-body').innerHTML=[...env_history].reverse().map((row,idx)=>{
    const cls=idx===0?'latest flash':'',pc=(row.profit||0)>=0?'pos':'neg';
    return'<tr class="'+cls+'"><td class="neu">Q'+row.quarter+'</td>'+
      '<td style="color:#aaa">'+(row.action||'').replace('_',' ')+'</td>'+
      '<td class="'+pc+'">'+fmt$(row.profit||0)+'</td>'+
      '<td class="info">'+((row.market_share||0)*100).toFixed(1)+'%</td>'+
      '<td>'+rankStr(row.market_rank||3)+'</td>'+
      '<td style="color:#586069;font-size:10px">'+(row.event||'—')+'</td></tr>';
  }).join('');

  const feed=d.news_feed||[];
  if(feed.length)document.getElementById('news-ticker-inner').textContent=
    feed.map(f=>'Q'+f.q+': '+f.text).join('   ◆   ');

  ['badge-rev','badge-share','badge-comp'].forEach(id=>{
    document.getElementById(id).textContent='Q'+(d.quarter||0);
  });

  if(d.done){
    document.getElementById('gameover-msg').textContent=(d.message||'').includes('💀')?'💀 GAME OVER':'🏆 SIMULATION COMPLETE';
    document.getElementById('gameover-sub').textContent=d.message||'';
    document.getElementById('gameover').classList.add('show');
  }
}

async function fetchState(){
  const[sr,hr]=await Promise.all([fetch('/api/state'),fetch('/api/history')]);
  const d=await sr.json(),hd=await hr.json();
  env_history=hd.history||[];d.history=env_history;updateUI(d);
}
async function doStep(action){
  const amount=parseFloat(document.getElementById('amount-input').value)||5000;
  const r=await fetch('/api/step',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,amount})});
  const d=await r.json(),hr=await fetch('/api/history'),hd=await hr.json();
  env_history=hd.history||[];d.history=env_history;updateUI(d);
}
async function doReset(){
  document.getElementById('gameover').classList.remove('show');
  env_history=[];
  const task=document.getElementById('task-select').value;
  const r=await fetch('/api/reset',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({task,seed:Math.floor(Math.random()*10000)})});
  const d=await r.json();
  chartRev.data.labels=[];chartRev.data.datasets[0].data=[];chartRev.data.datasets[1].data=[];chartRev.update();
  document.getElementById('history-body').innerHTML='';updateUI(d);
}
function updateClock(){document.getElementById('clock').textContent=new Date().toTimeString().slice(0,8)}
setInterval(updateClock,1000);updateClock();
fetchState();
</script>
</body>
</html>"""


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    uvicorn.run("app:main", host="0.0.0.0", port=7860, reload=False)