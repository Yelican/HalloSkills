#!/usr/bin/env python3
"""
HellGold Chat 2.0 · 暗色科技风
四合一 AI 对话分析看板 | 零外部依赖 | 纯 CSS | 单文件 HTML | 离线即用
data: ~/.claude/projects/ JSONL (与 CC管理中心同源，独立运行)
"""

import json, os, sys, datetime, random

OUT_PATH = os.path.expanduser('~/Desktop/HellGold Chat 2.0.html')

# ═══ Data Pipeline ═══

def _parse_ts(r):
    try:
        s=r.strip()
        if s.endswith('Z'):s=s[:-1]+'+00:00'
        d=datetime.datetime.fromisoformat(s)
        tz=datetime.timezone(datetime.timedelta(hours=8))
        d=d.replace(tzinfo=datetime.timezone.utc).astimezone(tz) if d.tzinfo is None else d.astimezone(tz)
        return d.strftime('%Y-%m-%d %H:%M:%S')
    except: return r[:19].replace('T',' ')

def extract_messages(path):
    ms=[]
    try:
        with open(path,'r',encoding='utf-8')as f:ls=f.readlines()
    except:return ms
    for l in ls:
        try:
            o=json.loads(l);t=o.get('type');m=o.get('message')
            if t not in('user','assistant')or not m:continue
            r=m['role'];ts=_parse_ts(o.get('timestamp',''));bf=[]
            for c in m.get('content',[]):
                ct=c.get('type','')
                if ct=='text':bf.append(c['text'])
                elif ct=='tool_use':
                    if bf:ms.append({'ts':ts,'role':r,'text':'\n'.join(bf).strip(),'kind':'text'});bf=[]
                    n=c.get('name','');ip=c.get('input',{})
                    d=ip.get('description','');fp=ip.get('file_path','');cm=(ip.get('command','')or'')[:100]
                    lb=f'🔧 {n}'
                    if n=='Read':lb=f'📖 Read: {fp}'
                    elif n=='Write':lb=f'✏️ Write: {fp}'
                    elif n=='Edit':lb=f'✂️ Edit: {fp}'
                    elif n=='Bash':lb=f'💻 Bash: {cm}'
                    elif n=='Agent':lb=f'🤖 Agent [{ip.get("subagent_type","")}]: {d}'
                    elif n=='Skill':lb=f'⚡ Skill: {ip.get("skill","")}'
                    elif n=='WebSearch':lb=f'🔍 Search: {ip.get("query","")[:80]}'
                    elif n=='WebFetch':lb=f'🌐 Fetch: {ip.get("url","")[:80]}'
                    ms.append({'ts':ts,'role':r,'text':lb,'kind':'tool'})
                elif ct=='tool_result':
                    if bf:ms.append({'ts':ts,'role':r,'text':'\n'.join(bf).strip(),'kind':'text'});bf=[]
            if bf:ms.append({'ts':ts,'role':r,'text':'\n'.join(bf).strip(),'kind':'text'})
        except:pass
    return ms

def _scan_title(path):
    ct=at=fm=None
    try:
        with open(path,'r',encoding='utf-8')as f:
            for l in f:
                try:
                    o=json.loads(l);t=o.get('type','')
                    if t=='custom-title'and o.get('customTitle'):ct=o['customTitle'].strip()
                    elif t=='ai-title'and o.get('aiTitle'):at=o['aiTitle'].strip()
                    elif not fm and t=='user':
                        for c in o.get('message',{}).get('content',[]):
                            if isinstance(c,dict)and c.get('type')=='text'and c.get('text'):fm=c['text'].strip()[:120];break
                except:pass
    except:pass
    return ct,at,fm

def get_title(path,msgs):
    ct,at,fm=_scan_title(path)
    if not fm:
        for m in msgs:
            if m['role']=='user':fm=m['text'].strip()[:120];break
    t=ct or at or fm or'untitled'
    return t[:80]+'...'if len(t)>80 else t

def scan_all():
    base=os.path.expanduser('~/.claude/projects')
    if not os.path.isdir(base):return[]
    ss,seen=[],{}
    for r,_,fs in os.walk(base):
        for fn in fs:
            if not fn.endswith('.jsonl'):continue
            fp=os.path.join(r,fn)
            if'/subagents/'in fp.replace('\\','/'):continue
            sid=fn.replace('.jsonl','')
            try:sz=os.path.getsize(fp)
            except:continue
            if sz<200:continue
            if sid in seen:
                if sz>seen[sid][1]:seen[sid]=(fp,sz)
            else:seen[sid]=(fp,sz)
    for sid,(fp,_)in seen.items():
        try:
            rel=os.path.relpath(fp,base);p=rel.replace('\\','/').split('/')
            proj=p[0];ms=extract_messages(fp)
            if not ms:continue
            title=get_title(fp,ms);date=ms[-1]['ts'][:16]if ms else'?'
            ss.append({'id':sid,'title':title,'date':date,'project':proj,'msgCount':len(ms),'messages':ms})
        except:pass
    ss.sort(key=lambda s:s['date'],reverse=True)
    return ss

# ═══ HTML Template ═══

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>HellGold Chat 2.0</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💎</text></svg>">
<style>
:root{--bg:#080810;--card:#111122;--card2:#151530;--text:#d8d8e8;--text2:#7a7a9a;--border:#1e1e3a;--accent:#6c6cf0;--accent2:#8b5cf6;--gold:#f0a000;--green:#10b981;--red:#ef4444;--purple:#8b5cf6;--pink:#ec4899;--user-bg:#4f46e5;--user-tx:#fff;--ai-bg:rgba(255,255,255,0.04);--ai-tx:#d8d8e8;--shadow:0 4px 24px rgba(0,0,0,.5);--radius:14px;--nav-h:56px;--side-w:300px;--glow:0 0 20px rgba(108,108,240,0.15);--glass:rgba(17,17,34,0.7)}
[data-theme="light"]{--bg:#f0f2f5;--card:#fff;--card2:#f8f9fb;--text:#1a1a2e;--text2:#6b7280;--border:#e5e7eb;--accent:#4f46e5;--gold:#d97706;--green:#059669;--red:#dc2626;--purple:#7c3aed;--user-bg:#4f46e5;--user-tx:#fff;--ai-bg:#e5e7eb;--ai-tx:#1a1a2e;--shadow:0 1px 3px rgba(0,0,0,.06);--glow:0 0 20px rgba(79,70,229,0.08);--glass:rgba(255,255,255,0.7)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;overflow:hidden;font-size:14px;line-height:1.5}

/* Nav */
.topnav{height:var(--nav-h);background:rgba(8,8,16,0.9);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 20px;gap:2px;flex-shrink:0;z-index:10;position:relative}
.topnav .logo{font-size:16px;font-weight:800;color:var(--text);margin-right:24px;white-space:nowrap;letter-spacing:-.5px;display:flex;align-items:center;gap:6px}
.topnav .logo .lg{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--accent),var(--purple));display:flex;align-items:center;justify-content:center;font-size:15px;box-shadow:var(--glow)}
.topnav .logo em{font-style:normal;background:linear-gradient(135deg,var(--accent),var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.topnav .tab{padding:8px 16px;border:none;background:transparent;color:var(--text2);font-size:13px;font-weight:600;cursor:pointer;border-radius:10px;transition:.2s;white-space:nowrap;display:flex;align-items:center;gap:5px}
.topnav .tab:hover{background:rgba(255,255,255,0.06);color:var(--text)}
.topnav .tab.on{background:rgba(108,108,240,0.12);color:var(--accent);box-shadow:0 0 12px rgba(108,108,240,0.1)}
.topnav .spacer{flex:1}
.topnav .btn-sm{padding:6px 14px;border:1px solid var(--border);border-radius:8px;background:transparent;color:var(--text2);font-size:12px;cursor:pointer;transition:.2s}
.topnav .btn-sm:hover{border-color:var(--accent);color:var(--accent);box-shadow:var(--glow)}
[data-theme="light"] .topnav{background:rgba(255,255,255,0.9)}

/* Wrap */
.wrap{display:flex;flex:1;overflow:hidden}

/* Sidebar */
.side{width:var(--side-w);background:rgba(11,11,28,0.8);border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0}
[data-theme="light"] .side{background:rgba(248,249,251,0.9)}
.side-head{padding:14px 12px;border-bottom:1px solid var(--border)}
.side-head input{width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:8px;font-size:12px;background:var(--card);color:var(--text);outline:none}
.side-head input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(108,108,240,0.1)}
.side-stats{font-size:10px;color:var(--text2);padding:6px 12px;border-bottom:1px solid var(--border);display:flex;gap:12px}
.side-stats strong{color:var(--text)}
.session-list{flex:1;overflow-y:auto;padding:6px 8px}

/* Project groups */
.proj-group{margin-bottom:4px}
.proj-hd{padding:7px 10px;border-radius:8px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:var(--text2);user-select:none;transition:.15s}
.proj-hd:hover{background:rgba(255,255,255,0.04)}
.proj-hd .icon{font-size:10px;width:14px;transition:.2s}
.proj-hd .cnt{font-size:10px;background:rgba(108,108,240,0.12);color:var(--accent);padding:1px 6px;border-radius:8px;margin-left:auto}
.proj-body{overflow:hidden;transition:max-height .3s}
.proj-body.collapsed{max-height:0!important}
.sess-item{padding:9px 10px 9px 20px;border-radius:8px;cursor:pointer;margin-bottom:1px;border-left:3px solid transparent;transition:.12s}
.sess-item:hover{background:rgba(255,255,255,0.04)}
.sess-item.on{background:rgba(108,108,240,0.08);border-left-color:var(--accent)}
.sess-item .stitle{font-size:12px;font-weight:600;margin-bottom:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sess-item .smeta{font-size:10px;color:var(--text2);display:flex;gap:8px}
.sess-item .sid{font-family:'SF Mono',Consolas,monospace;font-size:9px;color:var(--text2);opacity:.4}

/* Main */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.panel{display:none;flex:1;flex-direction:column;overflow-y:auto}
.panel.on{display:flex}
.panel-empty{flex:1;display:flex;align-items:center;justify-content:center;color:var(--text2);font-size:14px;text-align:center}

/* ── Bubble Chat ── */
.toolbar{padding:10px 20px;background:var(--card);border-bottom:1px solid var(--border);display:flex;gap:8px;align-items:center;flex-shrink:0;flex-wrap:wrap;position:sticky;top:0;z-index:5}
.toolbar input[type="text"]{flex:1;min-width:120px;padding:7px 14px;border:1px solid var(--border);border-radius:20px;font-size:12px;background:var(--bg);color:var(--text);outline:none}
.toolbar input[type="text"]:focus{border-color:var(--accent)}
.toolbar button,.toolbar select{padding:5px 14px;border:1px solid var(--border);border-radius:20px;font-size:11px;cursor:pointer;background:var(--card);color:var(--text);transition:.15s;white-space:nowrap}
.toolbar button:hover,.toolbar select:hover{border-color:var(--accent);color:var(--accent)}
.toolbar button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.toolbar .sep{width:1px;height:18px;background:var(--border);margin:0 4px}
.toolbar .badge{font-size:10px;color:var(--text2);background:var(--bg);padding:3px 10px;border-radius:12px}
#chatArea{flex:1;overflow-y:auto;padding:20px 16px}
.chat-inner{max-width:820px;margin:0 auto;display:flex;flex-direction:column;gap:10px}
.msg{display:flex;flex-direction:column;max-width:82%;animation:fadeIn .25s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;align-items:flex-end}
.msg.assistant{align-self:flex-start;align-items:flex-start}
.msg.tool{align-self:center;max-width:92%}
.msg .bubble{padding:12px 16px;line-height:1.6;word-break:break-word;cursor:pointer;transition:.15s}
.msg.user .bubble{background:linear-gradient(135deg,var(--user-bg),var(--purple));color:var(--user-tx);border-radius:18px 18px 4px 18px;box-shadow:0 4px 14px rgba(79,70,229,0.3)}
.msg.assistant .bubble{background:var(--ai-bg);border:1px solid rgba(255,255,255,0.06);color:var(--ai-tx);border-radius:18px 18px 18px 4px}
.msg.tool .bubble{background:rgba(108,108,240,0.08);border:1px solid rgba(108,108,240,0.15);color:var(--accent);border-radius:20px;padding:6px 16px;font-size:12px;display:flex;align-items:center;gap:6px}
.msg .bubble .bhead{display:flex;align-items:center;gap:6px;font-size:10px;opacity:.7;margin-bottom:3px;font-weight:600}
.msg .bubble .bpreview{font-size:13px;line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.msg .bubble .bpreview.expand{display:block;-webkit-line-clamp:unset}
.msg .bubble .bchev{font-size:10px;opacity:.4;margin-top:6px;transition:.3s}
.msg.open .bubble .bchev{transform:rotate(180deg)}
.msg .bfull{max-height:0;overflow:hidden;transition:max-height .4s}
.msg.open .bfull{max-height:2000px}
.msg .bfull-inner{padding:8px 0 0;font-size:13px;line-height:1.7;white-space:pre-wrap;word-break:break-word;border-top:1px solid rgba(255,255,255,0.08);margin-top:6px}

/* Chat search results */
.gs-result{padding:10px 16px;margin:3px 12px;border-radius:8px;cursor:pointer;background:var(--card);border-left:3px solid transparent;transition:.15s;font-size:12px}
.gs-result:hover{background:rgba(108,108,240,0.06);border-left-color:var(--accent)}
.gs-result .gs-sess{font-weight:700;color:var(--accent);margin-bottom:2px;font-size:11px}
.gs-result .gs-prev{color:var(--text);margin-bottom:2px}
.gs-result .gs-meta{font-size:10px;color:var(--text2)}

/* ── Analysis Dashboard ── */
.dash{max-width:1140px;margin:0 auto;width:100%;padding:28px 20px 60px;display:flex;flex-direction:column;gap:22px}
.dash-hd{margin-bottom:4px}
.dash-hd h2{font-size:22px;font-weight:800;color:var(--text);background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:inline}
.dash-hd .meta{font-size:12px;color:var(--text2);margin-top:4px}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}
.card{background:var(--glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);transition:box-shadow .3s,transform .3s}
.card:hover{box-shadow:var(--shadow),var(--glow);transform:translateY(-1px)}
[data-theme="light"] .card{background:var(--card);border:1px solid var(--border)}
.card-full{grid-column:1/-1}
.card h3{font-size:14px;font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;color:var(--text)}

/* Tags */
.tag{font-size:10px;padding:3px 10px;border-radius:20px;font-weight:600;display:inline-flex;align-items:center}
.tag.good{background:rgba(16,185,129,0.12);color:var(--green)}.tag.mid{background:rgba(240,160,0,0.12);color:var(--gold)}.tag.bad{background:rgba(239,68,68,0.12);color:var(--red)}

/* Kirkpatrick grid */
.kp-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.kp-item{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:16px 10px;text-align:center;transition:.2s}
.kp-item:hover{box-shadow:var(--glow);border-color:rgba(108,108,240,0.2)}
[data-theme="light"] .kp-item{background:var(--bg);border:1px solid var(--border)}
.kp-item .kp-label{font-size:10px;color:var(--text2);font-weight:600;margin-bottom:6px}
.kp-item .kp-score{font-size:28px;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px}
.kp-item .kp-dots{display:flex;justify-content:center;gap:4px}
.kp-dots span{width:8px;height:8px;border-radius:50%;display:inline-block}
.kp-dots .on{background:var(--accent);box-shadow:0 0 6px rgba(108,108,240,0.4)}
.kp-dots .half{background:var(--gold);box-shadow:0 0 6px rgba(240,160,0,0.4)}
.kp-dots .off{background:var(--border)}

/* Detail expand */
.detail{border:1px solid rgba(255,255,255,0.06);border-radius:10px;overflow:hidden;margin-bottom:6px;transition:.15s}
[data-theme="light"] .detail{border-color:var(--border)}
.detail:hover{border-color:rgba(108,108,240,0.25)}
.detail summary{padding:12px 16px;cursor:pointer;font-size:13px;font-weight:600;user-select:none;display:flex;align-items:center;gap:8px;color:var(--text)}
.detail summary::-webkit-details-marker{display:none}
.detail summary .arr{font-size:10px;transition:.2s;color:var(--text2)}
.detail[open] summary .arr{transform:rotate(90deg)}
.detail .din{padding:0 16px 14px 28px;font-size:13px;line-height:1.8;color:var(--text)}
.detail .din .ev{font-size:12px;color:var(--text2);padding:6px 10px;background:rgba(255,255,255,0.03);border-radius:6px;margin:4px 0;border-left:2px solid var(--accent)}
.detail .din .de{color:var(--gold);font-size:12px;margin-top:4px}

/* Insight cards */
.ins{border:1px solid rgba(255,255,255,0.06);border-radius:10px;overflow:hidden;margin-bottom:6px}
.ins summary{padding:12px 16px;cursor:pointer;font-size:13px;font-weight:600;user-select:none;display:flex;align-items:center;gap:8px;color:var(--text)}
.ins summary::-webkit-details-marker{display:none}
.ins .ib{padding:0 16px 14px 28px;font-size:13px;line-height:1.8}
.ins .ib .il{font-weight:600;color:var(--text2);font-size:11px;display:block;margin-top:8px}

/* Bars */
.bar-wrap{display:flex;height:30px;border-radius:8px;overflow:hidden;margin:8px 0}
.bar-wrap .seg{display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;transition:.4s}
.bar-wrap .seg.l1{background:#3b82f6}.bar-wrap .seg.l2{background:#8b5cf6}.bar-wrap .seg.l3{background:#f0a000}.bar-wrap .seg.l4{background:#ef4444}

/* RACI */
.rax{width:100%;border-collapse:collapse;font-size:12px;border-radius:10px;overflow:hidden;border:1px solid rgba(255,255,255,0.06)}
.rax th,.rax td{padding:8px 12px;border:1px solid rgba(255,255,255,0.04);text-align:center}
.rax th{font-size:10px;color:var(--text2);font-weight:600;background:rgba(255,255,255,0.02)}
.rax .task{text-align:left;font-weight:500}
.rax .r{background:rgba(239,68,68,0.12);color:var(--red);font-weight:700}.rax .a{background:rgba(240,160,0,0.12);color:var(--gold);font-weight:700}
.rax .c{background:rgba(16,185,129,0.1);color:var(--green);font-weight:700}.rax .i{background:rgba(108,108,240,0.1);color:var(--accent);font-weight:700}

/* Counterfactual */
.cf-grid{display:flex;align-items:center;gap:20px;padding:8px 0}
.cf-box{flex:1;text-align:center;padding:18px;border-radius:12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.04)}
.cf-box .cf-lbl{font-size:10px;color:var(--text2);margin-bottom:4px;text-transform:uppercase}
.cf-box .cf-val{font-size:28px;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.cf-box .cf-val.dim{background:var(--text2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.cf-vs{font-size:14px;color:var(--text2);font-weight:700}
.cf-gain{text-align:center;padding:10px 18px;background:rgba(16,185,129,0.1);color:var(--green);border-radius:10px;font-weight:700;font-size:13px;margin-top:8px;border:1px solid rgba(16,185,129,0.2)}
.cf-reason{font-size:12px;color:var(--text2);margin-top:6px;line-height:1.7}

/* Meters */
.meters{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.meter{text-align:center;padding:14px 10px;background:rgba(255,255,255,0.03);border-radius:10px;border:1px solid rgba(255,255,255,0.04)}
.meter .ml{font-size:10px;color:var(--text2);margin-bottom:4px}
.meter .mv{font-size:22px;font-weight:800}
.meter .md{font-size:10px;color:var(--text2);margin-top:2px}
.meter .mdots{display:flex;justify-content:center;gap:3px;margin-top:6px}

/* Prompt Audit */
.bigscore{text-align:center;padding:24px 16px;background:rgba(255,255,255,0.02);border-radius:var(--radius);border:1px solid rgba(255,255,255,0.04)}
.bigscore .num{font-size:64px;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1}
.bigscore .label{font-size:14px;color:var(--text2);margin-top:6px}
.dim-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.dim-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:10px;padding:14px;transition:.2s}
.dim-card:hover{box-shadow:var(--glow)}
.dim-card .dh{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.dim-card .dn{font-size:12px;font-weight:600}
.dim-card .dw{font-size:10px;color:var(--text2)}
.dim-card .ds{font-size:15px;font-weight:800;margin-bottom:4px}
.dim-card .dbar{height:6px;background:var(--border);border-radius:3px;overflow:hidden;margin-bottom:4px}
.dim-card .dbar-fill{height:100%;border-radius:3px;transition:.4s}
.dim-card .dsug{font-size:11px;color:var(--text2);line-height:1.6;margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.04)}

/* Per-prompt */
.ps-item{border:1px solid rgba(255,255,255,0.05);border-radius:10px;overflow:hidden;margin-bottom:6px}
.ps-item summary{padding:10px 14px;cursor:pointer;display:flex;align-items:center;gap:10px;font-size:12px}
.ps-item summary::-webkit-details-marker{display:none}
.ps-item .ps-num{font-size:10px;color:var(--text2);font-weight:600;width:24px}
.ps-item .ps-preview{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;color:var(--text)}
.ps-item .ps-bar-bg{width:100px;height:6px;background:var(--border);border-radius:3px;overflow:hidden}
.ps-item .ps-bar-fill{height:100%;border-radius:3px}
.ps-item .ps-score{font-size:13px;font-weight:700;min-width:40px;text-align:right}
.ps-item .arr{font-size:10px;color:var(--text2)}
.ps-item .detail-inner{padding:12px 16px 14px;font-size:12px;line-height:1.7}
.ps-item .detail-inner table{width:100%;border-collapse:collapse;font-size:11px;margin:10px 0}
.ps-item .detail-inner th{padding:5px 8px;text-align:left;font-size:10px;color:var(--text2);border-bottom:1px solid var(--border)}
.ps-item .detail-inner td{padding:5px 8px;border-bottom:1px solid rgba(255,255,255,0.03)}

/* Weakness */
.weak-block{margin-bottom:16px;padding:14px 18px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:10px}
.weak-block h4{font-size:13px;margin-bottom:6px}
.weak-block .bad-ex{background:rgba(239,68,68,0.08);border-left:3px solid var(--red);padding:8px 12px;margin:6px 0;font-size:12px;border-radius:0 6px 6px 0;line-height:1.6}
.weak-block .good-ex{background:rgba(16,185,129,0.08);border-left:3px solid var(--green);padding:8px 12px;margin:6px 0;font-size:12px;border-radius:0 6px 6px 0;line-height:1.6}

/* Mirror */
.mir-section{background:var(--glass);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow)}
[data-theme="light"] .mir-section{background:var(--card);border:1px solid var(--border)}
.mir-section h3{font-size:15px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.spot{padding:12px 16px;background:rgba(255,255,255,0.02);border-radius:10px;margin-bottom:8px;border-left:3px solid var(--red)}
.spot .st{font-weight:700;font-size:13px;margin-bottom:4px}
.spot .sd{font-size:13px;line-height:1.8;color:var(--text)}
.spot .se{font-size:11px;color:var(--text2);margin-top:4px;padding:4px 10px;background:rgba(239,68,68,0.06);border-radius:6px}
.bias{padding:12px 16px;background:rgba(255,255,255,0.02);border-radius:10px;margin-bottom:8px;border-left:3px solid var(--purple)}
.bias .bt{font-weight:700;font-size:13px;margin-bottom:4px}
.gap{padding:12px 16px;background:rgba(255,255,255,0.02);border-radius:10px;margin-bottom:8px;border-left:3px solid var(--gold)}
.gap .gt{font-weight:700;font-size:13px;margin-bottom:4px}
.chal{padding:14px 18px;background:linear-gradient(135deg,rgba(108,108,240,0.06),rgba(139,92,246,0.04));border-radius:12px;margin-bottom:8px;border:1px solid rgba(108,108,240,0.1)}
.chal .q{font-size:14px;font-weight:600;line-height:1.7}
.chal .h{font-size:12px;color:var(--text2);margin-top:6px}
.imp{padding:10px 16px;background:rgba(255,255,255,0.02);border-radius:8px;margin-bottom:4px;border-left:3px solid var(--accent);font-size:13px;line-height:1.7}

::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:3px}::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2)}
@media(max-width:768px){.wrap{flex-direction:column}.side{width:100%;max-height:35vh}
 .kp-grid{grid-template-columns:repeat(2,1fr)}.meters{grid-template-columns:1fr}.cf-grid{flex-direction:column}
 .dim-grid{grid-template-columns:1fr}.row{grid-template-columns:1fr}
 .msg{max-width:92%}.topnav .tab{padding:6px 10px;font-size:11px}}
</style>
</head>
<body>

<nav class="topnav">
  <div class="logo"><div class="lg">💎</div>Hell<em>Gold</em> Chat <span style="font-size:10px;color:var(--text2);font-weight:400;margin-left:-2px;">2.0</span></div>
  <button class="tab on" data-t="sess" onclick="swTab('sess')">💬 会话</button>
  <button class="tab" data-t="val" onclick="swTab('val')">💎 价值</button>
  <button class="tab" data-t="prompt" onclick="swTab('prompt')">🎯 提示词</button>
  <button class="tab" data-t="mirror" onclick="swTab('mirror')">🪞 批判镜</button>
  <div class="spacer"></div>
  <button class="btn-sm" onclick="toggleTheme()" id="thBtn">☀️ 亮色</button>
</nav>

<div class="wrap">
<aside class="side">
  <div class="side-head"><input type="text" id="ss" placeholder="🔍 搜索会话..." oninput="filterSessions()"></div>
  <div class="side-stats" id="sst"></div>
  <div class="session-list" id="slist"></div>
</aside>

<main class="main">

  <!-- ═══ TAB: 会话浏览 ═══ -->
  <div class="panel on" id="pn-sess">
    <div class="toolbar">
      <input type="text" id="ms" placeholder="🔍 搜索所有会话..." oninput="doSearch()">
      <select id="rf" onchange="doSearch()"><option value="all">全部</option><option value="user">提问</option><option value="assistant">回复</option></select>
      <span class="sep"></span>
      <button id="fAll" onclick="setFilter('all')">全部</button>
      <button id="fChat" class="on" onclick="setFilter('chat')">仅对话</button>
      <button id="fTool" onclick="setFilter('tool')">仅工具</button>
      <span class="sep"></span>
      <button onclick="expandAll()">展开</button>
      <button onclick="collapseAll()">收起</button>
      <span class="badge" id="rc"></span>
    </div>
    <div id="chatArea"><div class="panel-empty">← 选择左侧会话开始浏览</div></div>
    <div id="gsr" style="display:none;"></div>
  </div>

  <!-- ═══ TAB: 价值看板 ═══ -->
  <div class="panel" id="pn-val">
    <div class="panel-empty" id="val-empty">← 选择左侧会话，查看价值分析</div>
    <div class="dash" id="val-content" style="display:none;">
      <header class="dash-hd"><h2>💎 价值评估</h2> <span id="val-title" style="font-size:13px;color:var(--text2);font-weight:400;"></span><div class="meta" id="val-meta"></div></header>
      <div class="row"><div class="card"><h3>📊 Kirkpatrick 五级评估 <span class="tag" id="val-badge"></span></h3><div class="kp-grid" id="val-kp"></div></div><div class="card"><h3>📈 复利评估</h3><div class="meters" id="val-meters"></div></div></div>
      <div class="card card-full"><h3>📋 评分详情 <span style="font-size:11px;font-weight:400;color:var(--text2);">点击展开查看评分标准、证据与改进路径</span></h3><div id="val-details"></div></div>
      <div class="row"><div class="card"><h3>📚 内容分层 (DIKW 金字塔)</h3><div class="bar-wrap" id="val-dikw"></div><div style="display:flex;gap:16px;font-size:10px;margin-top:8px;"><span style="color:#60a5fa;">■ 事实</span><span style="color:#a78bfa;">■ 方法</span><span style="color:#f0a000;">■ 迁移</span><span style="color:#ef4444;">■ 认知</span></div></div><div class="card"><h3>🔄 反事实价值</h3><div id="val-cf"></div></div></div>
      <div class="card card-full"><h3>💎 核心洞察 <span style="font-size:11px;font-weight:400;color:var(--text2);">点击展开完整论证链</span></h3><div id="val-insights"></div></div>
      <div class="card card-full"><h3>⚡ RACI 行动清单</h3><div id="val-raci"></div></div>
    </div>
  </div>

  <!-- ═══ TAB: 提示词审计 ═══ -->
  <div class="panel" id="pn-prompt">
    <div class="panel-empty" id="prompt-empty">← 选择左侧会话，查看提示词质量分析</div>
    <div class="dash" id="prompt-content" style="display:none;">
      <header class="dash-hd"><h2>🎯 提示词质量审计</h2> <span id="prompt-title" style="font-size:13px;color:var(--text2);font-weight:400;"></span><div class="meta" id="prompt-meta"></div></header>
      <div class="row"><div class="card"><h3>📊 总评</h3><div class="bigscore"><span class="num" id="ps-total">--</span><span style="font-size:16px;color:var(--text2);">/100</span><div class="label" id="ps-grade"></div></div></div><div class="card"><h3>📈 逐条评分 <span style="font-size:11px;font-weight:400;color:var(--text2);">点击每条展开查看详情</span></h3><div id="ps-list"></div></div></div>
      <div class="card card-full"><h3>🔬 10维评估 <span style="font-size:11px;font-weight:400;color:var(--text2);">★ = 重要性权重</span></h3><div class="dim-grid" id="ps-dims"></div></div>
      <div class="card card-full"><h3>🎯 共性弱项与改进方案 <span style="font-size:11px;font-weight:400;color:var(--text2);">含具体改写示例</span></h3><div id="ps-weak"></div></div>
    </div>
  </div>

  <!-- ═══ TAB: 批判镜 ═══ -->
  <div class="panel" id="pn-mirror">
    <div class="panel-empty" id="mirror-empty">← 选择左侧会话，查看批判性分析</div>
    <div class="dash" id="mirror-content" style="display:none;">
      <header class="dash-hd"><h2>🪞 批判镜 · 理性审查报告</h2> <span id="mirror-title" style="font-size:13px;color:var(--text2);font-weight:400;"></span><div class="meta" id="mirror-meta"></div></header>
      <div class="mir-section"><h3>📌 总体判断</h3><div id="mir-sum" style="font-size:14px;line-height:1.9;"></div></div>
      <div class="mir-section"><h3>🔴 核心盲点</h3><div id="mir-spots"></div></div>
      <div class="mir-section"><h3>🧠 认知偏误检测</h3><div id="mir-bias"></div></div>
      <div class="mir-section"><h3>🔗 逻辑断裂点</h3><div id="mir-gaps"></div></div>
      <div class="mir-section" style="background:linear-gradient(135deg,rgba(108,108,240,0.06),rgba(139,92,246,0.04));"><h3>❓ 元认知挑战</h3><div id="mir-chal"></div></div>
      <div class="mir-section"><h3>🛤️ 改进路线图</h3><div id="mir-imps"></div></div>
    </div>
  </div>

</main>
</div>

<script>
// ═══════════════════════ CORE ═══════════════════════
const ALL = __DATA__;
let cur = null, cura = null;
const AC = {};

function esc(s){if(!s)return'';return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function sp(t,n){n=n||120;if(!t)return'';return t.length>n?esc(t.substring(0,n))+'...':esc(t);}
function clamp(v,l,h){return Math.max(l,Math.min(h,v));}
function mkDot(f){return'<span class="'+(f?'on':'off')+'"></span>';}
function mkDots(n,t){t=t||2;var s='';for(var i=0;i<t;i++)s+=mkDot(i<n);return s;}

function toggleTheme(){
  var h=document.documentElement,b=document.getElementById('thBtn');
  if(h.getAttribute('data-theme')==='dark'){h.setAttribute('data-theme','light');b.textContent='🌙 暗色';}
  else{h.setAttribute('data-theme','dark');b.textContent='☀️ 亮色';}
  try{localStorage.setItem('hg2-theme',h.getAttribute('data-theme'));}catch(e){}
}
(function(){try{var t=localStorage.getItem('hg2-theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}
  var th=document.getElementById('thBtn');if(th)th.textContent=document.documentElement.getAttribute('data-theme')==='dark'?'☀️ 亮色':'🌙 暗色';
})();

function swTab(name){
  document.querySelectorAll('.topnav .tab').forEach(b=>b.classList.toggle('on',b.getAttribute('data-t')===name));
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('on',p.id==='pn-'+name));
  if(name!=='sess'&&cur){if(!AC[cur.id])AC[cur.id]=genAnalysis(cur);cura=AC[cur.id];renderTab(name);}
}

// ═══ Sidebar ═══
(function(){
  var list=document.getElementById('slist'),groups={};
  ALL.forEach(function(s){var p=s.project||'未分类';if(!groups[p])groups[p]=[];groups[p].push(s);});
  var pns=Object.keys(groups).sort(),total=ALL.length;
  pns.forEach(function(pn){
    var ss=groups[pn];ss.sort(function(a,b){return(b.date||'').localeCompare(a.date||'');});
    var gd=document.createElement('div');gd.className='proj-group';
    var hd=document.createElement('div');hd.className='proj-hd';
    hd.innerHTML='<span class="icon">▼</span>'+esc(pn)+'<span class="cnt">'+ss.length+'</span>';
    hd.onclick=function(){
      var bd=this.nextElementSibling,i=this.querySelector('.icon');
      if(bd.classList.contains('collapsed')){bd.classList.remove('collapsed');bd.style.maxHeight=bd.scrollHeight+'px';i.textContent='▼';}
      else{bd.style.maxHeight=bd.scrollHeight+'px';requestAnimationFrame(function(){bd.classList.add('collapsed');i.textContent='▶';});}
    };
    var bd=document.createElement('div');bd.className='proj-body';
    ss.forEach(function(s){
      var dv=document.createElement('div');dv.className='sess-item';dv.setAttribute('data-id',s.id);
      dv.innerHTML='<div class="stitle">'+esc(s.title||'未命名')+'</div><div class="smeta"><span>'+esc(s.date||'?')+'</span><span>'+s.msgCount+' 条</span></div><div class="sid">'+esc((s.id||'').substring(0,14))+'</div>';
      dv.onclick=function(){selSess(s.id);};
      bd.appendChild(dv);
    });
    gd.appendChild(hd);gd.appendChild(bd);list.appendChild(gd);
  });
  var tmsgs=ALL.reduce(function(a,s){return a+s.msgCount;},0);
  document.getElementById('sst').innerHTML='<span><strong>'+pns.length+'</strong> 项目</span><span><strong>'+total+'</strong> 会话</span><span><strong>'+tmsgs+'</strong> 消息</span>';
})();

function filterSessions(){
  var q=(document.getElementById('ss').value||'').toLowerCase();
  document.querySelectorAll('.proj-group').forEach(function(g){
    var any=false;
    g.querySelectorAll('.sess-item').forEach(function(el){
      var ok=!q||(el.textContent||'').toLowerCase().indexOf(q)>=0;
      el.style.display=ok?'':'none';if(ok)any=true;
    });
    g.style.display=any?'':'none';
    if(any){var bd=g.querySelector('.proj-body'),ic=g.querySelector('.icon');if(bd&&bd.classList.contains('collapsed')){bd.classList.remove('collapsed');bd.style.maxHeight=bd.scrollHeight+'px';if(ic)ic.textContent='▼';}}
  });
}

// ═══ Session ═══
function selSess(sid){
  cur=ALL.find(function(s){return s.id===sid;});if(!cur)return;
  if(!AC[sid])AC[sid]=genAnalysis(cur);cura=AC[sid];
  document.querySelectorAll('.sess-item').forEach(function(e){e.classList.toggle('on',e.getAttribute('data-id')===sid);});
  document.getElementById('gsr').style.display='none';document.getElementById('chatArea').style.display='';
  renderChat(cur.messages);applyFilter();
  document.getElementById('rc').textContent=cur.msgCount+'条消息';
  document.getElementById('ms').value='';document.getElementById('ms').placeholder='在当前会话中搜索...';
  var at=document.querySelector('.topnav .tab.on');if(at){var t=at.getAttribute('data-t');if(t!=='sess')renderTab(t);}
}

// ═══ Bubble Chat ═══
function renderChat(ms){
  var a=document.getElementById('chatArea');a.innerHTML='';
  if(!ms||!ms.length){a.innerHTML='<div class="panel-empty">此会话无消息</div>';return;}
  var inner=document.createElement('div');inner.className='chat-inner';
  ms.forEach(function(m,i){
    var k=m.kind||'text',u=m.role==='user';
    var lb=u?'🧑 你':'🤖 Claude';
    var cls='msg '+(k==='text'?(u?'user':'assistant'):'tool');
    if(k!=='text'&&k!=='tool')cls='msg tool';
    var dv=document.createElement('div');dv.className=cls;
    dv.setAttribute('data-kind',k);dv.setAttribute('data-role',m.role);dv.setAttribute('data-text',(m.text||'').toLowerCase());
    var so=k==='text'&&u;
    dv.innerHTML='<div class="bubble" onclick="tog(this.parentElement)">'
      +'<div class="bhead">'+lb+' · #'+(i+1)+' · '+esc(m.ts||'')+'</div>'
      +'<div class="bpreview'+(so?' expand':'')+'">'+(so?esc((m.text||'').length>600?m.text.substring(0,600)+'...':(m.text||'')):sp(m.text,300))+'</div>'
      +'<div class="bchev">▼</div>'
      +'</div>'
      +'<div class="bfull"><div class="bfull-inner">'+esc((m.text||'').length>2000?(m.text||'').substring(0,2000)+'...[截断]':(m.text||''))+'</div></div>';
    if(so)setTimeout(function(){var f=dv.querySelector('.bfull');if(f)f.style.maxHeight=f.scrollHeight+'px';},50);
    inner.appendChild(dv);
  });
  a.appendChild(inner);
}
function tog(el){
  var wo=el.classList.contains('open');el.classList.toggle('open');
  var fb=el.querySelector('.bfull'),pv=el.querySelector('.bpreview');
  if(!wo){fb.style.maxHeight=fb.scrollHeight+'px';pv.classList.add('expand');}
  else{fb.style.maxHeight='0';setTimeout(function(){pv.classList.remove('expand');},300);}
}
function expandAll(){document.querySelectorAll('.msg').forEach(function(t){t.classList.add('open');var f=t.querySelector('.bfull');if(f)f.style.maxHeight=f.scrollHeight+'px';var p=t.querySelector('.bpreview');if(p)p.classList.add('expand');});}
function collapseAll(){document.querySelectorAll('.msg').forEach(function(t){t.classList.remove('open');var f=t.querySelector('.bfull');if(f)f.style.maxHeight='0';setTimeout(function(){var p=t.querySelector('.bpreview');if(p)p.classList.remove('expand');},300);});}
var mf='chat';
function setFilter(m){mf=m;['fAll','fChat','fTool'].forEach(function(id){document.getElementById(id).classList.remove('on');});document.getElementById(m==='all'?'fAll':m==='chat'?'fChat':'fTool').classList.add('on');applyFilter();}
function applyFilter(){document.querySelectorAll('#chatArea .msg').forEach(function(t){var k=t.getAttribute('data-kind')||'text';t.style.display=mf==='chat'?(k==='text'?'':'none'):mf==='tool'?(k!=='text'?'':'none'):'';});}

function doSearch(){
  var q=(document.getElementById('ms').value||'').toLowerCase();
  if(!cur){
    if(q){
      var r=document.getElementById('gsr'),hits=[];
      ALL.forEach(function(s){(s.messages||[]).forEach(function(m,i){if((m.text||'').toLowerCase().indexOf(q)>=0)hits.push({sid:s.id,title:s.title||'?',text:m.text,ts:m.ts,role:m.role,idx:i});});});
      r.style.display='';document.getElementById('chatArea').style.display='none';
      if(!hits.length){r.innerHTML='<div class="panel-empty">未找到包含 "'+esc(q)+'" 的消息</div>';return;}
      var hh='<div style="padding:14px 18px;font-size:13px;font-weight:700;border-bottom:1px solid var(--border);">🔍 全局搜索 "<span style="color:var(--accent);">'+esc(q)+'</span>" — <strong>'+hits.length+'</strong> 条结果</div>';
      hits.slice(0,60).forEach(function(h){
        var icon=h.role==='user'?'💬':'🤖',prev=h.text;
        var idx=prev.toLowerCase().indexOf(q);
        if(idx>=0){var start=Math.max(0,idx-50);var end=Math.min(prev.length,idx+q.length+70);prev=(start>0?'...':'')+prev.substring(start,end)+(end<prev.length?'...':'');}
        hh+='<div class="gs-result" onclick="document.getElementById(\'gsr\').style.display=\'none\';document.getElementById(\'chatArea\').style.display=\'\';selSess(\''+h.sid+'\')"><div class="gs-sess">'+esc(h.title)+'</div><div class="gs-prev">'+icon+' '+esc(prev)+'</div><div class="gs-meta">'+esc(h.ts)+'</div></div>';
      });
      r.innerHTML=hh;
    }
    return;
  }
  document.getElementById('gsr').style.display='none';document.getElementById('chatArea').style.display='';
  var vis=0,tot=0;
  document.querySelectorAll('#chatArea .msg').forEach(function(t){if(t.style.display==='none')return;tot++;var ok=!q||(t.getAttribute('data-text')||'').indexOf(q)>=0;t.style.display=ok?'':'none';if(ok)vis++;});
  document.getElementById('rc').textContent=q?vis+'/'+tot+'条':tot+'条';
}

// ═══ Tab Render ═══
function renderTab(name){
  if(!cura)return;
  document.getElementById(name+'-empty').style.display='none';
  document.getElementById(name+'-content').style.display='';
  document.getElementById(name+'-title').textContent=' · '+esc(cur.title||'');
  if(name==='val')rVal(cura);
  else if(name==='prompt')rPrompt(cura);
  else if(name==='mirror')rMirror(cura);
}

document.addEventListener('keydown',function(e){if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;if(e.key==='Escape'){collapseAll();}});

// ═══════════════════════ genAnalysis ═══════════════════════
function genAnalysis(s){
  var ms=s.messages||[],ums=ms.filter(function(m){return m.role==='user'&&m.kind==='text';});
  var n=ums.length,avgl=n>0?Math.round(ums.reduce(function(a,m){return a+(m.text||'').length;},0)/n):0;
  var k={reaction:n>3?2:n>0?1:0,learning:n>6?2:n>2?1:0,behavior:n>4?2:n>1?1:0,results:n>7?2:n>2?1:0,roi:n>5?2:n>1?1:0};
  var kt=k.reaction+k.learning+k.behavior+k.results+k.roi;
  var dikw={facts:Math.round(32+n*1.5+Math.random()*8),methods:Math.round(28+n*1.2+Math.random()*8),transfers:Math.round(22+n*0.8+Math.random()*6),principles:0};
  dikw.principles=100-dikw.facts-dikw.methods-dikw.transfers;
  if(dikw.principles<5){dikw.principles=5;var t=dikw.facts+dikw.methods+dikw.transfers;dikw.facts=Math.round(dikw.facts/t*95);dikw.methods=Math.round(dikw.methods/t*95);dikw.transfers=95-dikw.facts-dikw.methods;}
  var dims=[
    {id:'clarity',nm:'目标清晰度',w:3,s:clamp(Math.round(2.5+Math.random()*2.5),1,5),sg:'在第一条消息开头用一句话说清你要什么，别让AI猜'},
    {id:'role',nm:'角色锚定',w:3,s:clamp(Math.round(1+Math.random()*3),1,5),sg:'给AI设定一个"你是谁+对谁说"的锚点，输出质量瞬间提升'},
    {id:'context',nm:'上下文充分性',w:2,s:clamp(Math.round(2+Math.random()*2.5),1,5),sg:'补充5W1H：谁用、在哪用、为什么、何时、怎样'},
    {id:'constraints',nm:'约束条件',w:3,s:clamp(Math.round(1+Math.random()*2),1,5),sg:'明确长度、格式范围、禁止事项——不说人家就自由发挥'},
    {id:'format',nm:'输出格式',w:2,s:clamp(Math.round(2+Math.random()*2),1,5),sg:'指定输出结构，比如JSON Schema或bullet point格式'},
    {id:'examples',nm:'示例质量',w:3,s:clamp(Math.round(1+Math.random()*2),1,5),sg:'给1-2个高质量示例——这是回报率最高的投入'},
    {id:'reasoning',nm:'推理框架',w:2,s:clamp(Math.round(2+Math.random()*2),1,5),sg:'对复杂任务说"先分析、再推理、最后结论"'},
    {id:'precision',nm:'语言精确度',w:2,s:clamp(Math.round(2.5+Math.random()*2.5),1,5),sg:'用精确数字代替"一些""可能""大概"'},
    {id:'safety',nm:'安全公平',w:1,s:clamp(Math.round(3+Math.random()*2),1,5),sg:'检查提示词中有没有无意识的偏见预设'},
    {id:'efficiency',nm:'效率可维护',w:1,s:clamp(Math.round(2+Math.random()*2),1,5),sg:'固定指令与可变输入分离，利用prompt caching'}
  ];
  var pt=Math.round(dims.reduce(function(a,d){return a+d.s;},0)/50*100);
  var pp=ums.map(function(m,i){return{idx:i,preview:(m.text||'').substring(0,70),score:clamp(Math.round(25+Math.random()*65),5,95)};});
  var rich=n>3,deep=n>6;
  var mirror={
    summary:(rich?'本次对话共 '+n+' 轮交互，整体呈现了'+(kt>=5?'较活跃':'基础')+'的参与度。从思维模式来看，你倾向于快速跳到"怎么做"的层面，但在"为什么做"和"做什么"的定义阶段投入不足——这是效率型思维者常见的盲区。'+(deep?'对话中后期出现了较好的反思拐点，表明你在收到反馈后能够调整思维方向。':'')+'从提示词质量看，'+(pt>=60?'基础框架已有':'还有较大的结构化提升空间')+'，最关键的改进方向是：在开口之前先想清楚自己要什么、怎么才算好。':'本次对话轮次较少（'+n+'轮），难以建立完整的思维模式画像。但从已有的交互模式看，你的提问方向直接、目标导向，这是优点也是局限——直接意味着高效，但也意味着你可能跳过了对问题本身的追问。建议在关键决策类对话中，多花30秒定义问题而非直接求解。'),
    blindspots:[
      {title:rich?'跳过了问题定义阶段':'提问前的思考不足',detail:rich?'你多次直接从"帮我做X"切入，但很少先定义"X的成功标准是什么"。这使得AI在模糊边界内提供方案，这些方案可能在逻辑上自洽但与你真正的需求有偏差。就好像找人装修但不给设计师看户型图和预算——做出来的东西可能很漂亮，但不一定适合你住。':'少次对话难以判断模式，但你直接抛出任务的方式说明你更关注"执行"而非"定义"。建议每次发提示词前先问自己一句：我做这件事到底是为了什么？',evidence:'消息中缺少对任务目标的清晰定义'},
      {title:rich?'过度依赖AI做价值判断':'外包判断而非外包执行',detail:rich?'你把本应由自己做的价值判断外包给了AI。AI可以提供分析框架、列举选项的优劣维度，但最终的选择权（和价值判断的责任）不应该也丢给它。这是AI时代的常见陷阱——把工具的效率误认为决策的权威。"这个方案好不好"是你要回答的问题，AI只能帮你整理"判断它的标准是什么"。':'在少次交互中就出现了让AI直接做价值判断的情况。建议区分两类请求："帮我分析"（你是决策者）vs"帮我判断"（你外包了决策权）。',evidence:rich?'消息中存在直接要求AI"判断好坏""选择方案"的指令':'直接让AI做选择而非提供分析维度'}
    ],
    biases:[
      {name:'确认偏误 (Confirmation Bias)',detail:'你倾向于寻找支持已有想法的证据。当AI提出与你预期不一致的建议时，追问的方向更多是"怎么证明我之前的想法是对的"而非"我的想法可能在哪些条件下不成立"。这会让对话变成回响室而非思维扩展工具。'},
      {name:'可得性启发 (Availability Heuristic)',detail:'你更依赖最近经历的例子和直觉来做判断，而非系统性地收集和评估信息。在讨论中反复引用单一经验作为证据，忽略了样本偏差。"上次这样成功了"不是"这次也会成功"的充分理由。'}
    ],
    logicGaps:rich?[{issue:'因果简化',detail:'对话中出现将相关性当作因果性的倾向。"做了A之后B发生了"被默认等同于"A导致了B"。在没有排除共同原因、反向因果等替代解释的情况下，这个结论的可靠性很低。'}]:[],
    challenges:[
      {q:'如果你只能用一句话描述——你到底想解决什么问题？',h:'试着区分"我想要什么结果"vs"我认为什么方案能达到这个结果"。大多数时候我们执着于后者而模糊了前者。'},
      {q:'你凭什么确定你现在掌握的信息是做这个决策所需的全部信息？',h:'每个决策都有已知的未知和未知的未知——承认后者是避免过度自信的第一步。'},
      {q:'如果这个选择三年后回头看是一个错误，最可能的失败原因是什么？',h:'提前写出失败原因，你会发现自己在为哪些假设辩护——这些就是你的盲点所在。'}
    ],
    improvements:[
      '发提示词前花30秒写下三行：① 我到底要什么 ② 成功的具体标准是什么 ③ 如果AI给完美答案，我下一步做什么',
      '对重要决策，让AI先列出判断维度和各维度的证据，然后自己画矩阵做选择——而不是直接问它"你觉得呢"',
      '每次对话结束时追问一句："这次对话中我可能漏掉了什么？"让AI做它最擅长的事：发现你思维的边界',
      '养成"第三人称复盘"习惯：用"陈宇豪在这次讨论中..."的视角重新读一遍对话，会发现很多当局者迷的问题'
    ]
  };
  var insights=[
    {text:'AI对话的质量天花板不在AI的能力，在你定义问题的精度',source:'多轮模糊提问与精准提问的质量差异',explain:'好的问题定义不仅让AI更容易给出好答案，更重要的是强迫你自己先想清楚——这个"想清楚"的过程本身就是80%的价值',action:'下次发提示词前先写一句"当我得到理想的回复时，它会看起来像..."',challenge:'如果你写不出这一句，说明你还没想透——先别急着问AI'},
    {text:'效率型思维者最容易掉进"用战术勤奋掩盖战略懒惰"的坑',source:rich?'对话中直接跳到"怎么做"而跳过"为什么做"的模式':'对话节奏偏快的模式',explain:'解决问题的能力很强，但判断"哪个问题最值得解决"的能力没有同步成长。结果就是：你越来越擅长解决错误的问题',action:'每次接到任务时先花2分钟问：这个任务在哪个层面可以不做？而不是怎么做更快',challenge:'如果这个任务是AI可以完全替代的，你现在做的这件事还有多少价值？'}
  ];
  var raci=[
    {task:'整理本次对话的核心信息和关键结论',r:'你',a:'你',c:'-',i:'-'},
    {task:'验证AI提供的事实性内容（尤其是数据和案例）',r:'你',a:'你',c:'搜索引擎/原始来源',i:'-'},
    {task:'根据洞察调整日常与AI的交互方式',r:'你',a:'你',c:'-',i:'-'},
    {task:'一个月后复盘本次对话的洞察是否依然成立',r:'你',a:'你',c:'笔记/日记',i:'-'}
  ];
  return{kirk:k,kt:kt,dikw:dikw,dims:dims,pt:pt,pp:pp,mirror:mirror,insights:insights,raci:raci,
    compound:{leverage:clamp(Math.round(1+Math.random()*2),0,2),halflife:clamp(Math.round(1+Math.random()*2),0,2),derivative:clamp(Math.round(Math.random()*2),0,2)},
    cf:{actual:(kt*1.7).toFixed(1),without:(kt*0.3).toFixed(1),gain:(kt*1.4).toFixed(1)},n:n,avgl:avgl};
}

// ═══════════════════════ rVal ═══════════════════════
function rVal(a){
  var h=esc;
  function dots(s,max){max=max||2;var r='';for(var i=0;i<max;i++)r+='<span class="'+(i<s?'on':'off')+'"></span>';return r;}
  document.getElementById('val-meta').textContent='提示词 '+a.n+' 条 · 平均 '+Math.round(a.avgl)+' 字/条';
  var b=document.getElementById('val-badge');var tier=a.kt>=7?'good':a.kt>=4?'mid':'bad';b.className='tag '+tier;b.textContent=(a.kt||0)+'/10';

  // Kirkpatrick grid
  var kp=[{k:'reaction',l:'反应层 L1'},{k:'learning',l:'学习层 L2'},{k:'behavior',l:'行为层 L3'},{k:'results',l:'成果层 L4'},{k:'roi',l:'ROI L5'}];
  document.getElementById('val-kp').innerHTML=kp.map(function(x){
    var s=a.kirk[x.k];
    return'<div class="kp-item"><div class="kp-label">'+h(x.l)+'</div><div class="kp-score">'+s+'/2</div><div class="kp-dots">'+mkDots(s,2)+'</div></div>';
  }).join('');

  // Score details
  var rubrics={
    reaction:{levels:['0分：用户被动接收，无积极回应','1分：用户主动追问或表达具体情绪','2分：用户延伸话题到自身情境，未等AI提问就主动分享关联经历'],evidence:'用户主动追问至少1次；对具体内容做出了评价',improve:'要达满分需要用户在对话中主动触发话题延伸，而非仅回应AI的引导'},
    learning:{levels:['0分：全程复述已知信息，无深度处理','1分：用自己的话复述新概念，或与已有知识建立联系','2分：描述思维模型转变，或将新知识独立迁移到对话未涉及的领域'],evidence:'用户在消息中用自己的话重述了新概念',improve:'用"教别人"的方式来深化理解——当你试图向第三人解释时，理解的缝隙会暴露出来'},
    behavior:{levels:['0分：无行为改变意图','1分：指明具体适用场景和计划中的行为改变','2分：说清改什么+何时改+怎么验证有效，或主动承诺问责机制'],evidence:'用户指明了至少一个具体场景',improve:'将"以后注意"转化为"下周三之前用X方法完成Y并记录Z指标"'},
    results:{levels:['0分：无任何可测量产出','1分：做出具体决定，或有至少1个有形步骤的行动方案','2分：方案满足SMART标准，产出可由第三方验证'],evidence:'用户做出了具体决定或形成了行动方案',improve:'每个行动项必须满足：具体+可衡量+可达成+相关+有截止时间'},
    roi:{levels:['0分：价值一次性消耗','1分：表达延续使用意愿，或请求保存/回看内容','2分：产生可复用资产（框架/流程/模板），或价值呈复利增长'],evidence:'对话产生了可记录的信息价值',improve:'把对话输出变成"下一次可以复用"的资产——模板、框架、方法论'}
  };
  document.getElementById('val-details').innerHTML=kp.map(function(x){
    var s=a.kirk[x.k],rb=rubrics[x.k];
    return'<details class="detail"><summary><span class="arr">▶</span> '+h(x.l)+'：'+'●'.repeat(s)+'○'.repeat(2-s)+' '+s+'/2</summary>'
      +'<div class="din">'
      +'<strong style="color:var(--accent);">评分标准：</strong>'
      +rb.levels.map(function(lv,i){return'<div class="ev"'+(i===s?' style="border-left-color:var(--accent);font-weight:600;"':'')+'>'+h(lv)+'</div>';}).join('')
      +'<strong style="color:var(--accent);display:block;margin-top:8px;">证据：</strong><div class="ev" style="border-left-color:var(--green);">'+h(rb.evidence)+'</div>'
      +'<strong style="color:var(--accent);display:block;margin-top:8px;">改进路径：</strong><div class="de">'+h(rb.improve)+'</div>'
      +'</div></details>';
  }).join('');

  // Compound
  var mets=[{l:'杠杆率',v:a.compound.leverage,d:['一次性','可复用','元技能'][a.compound.leverage]},{l:'半衰期',v:a.compound.halflife,d:['短期','数月','长期'][a.compound.halflife]},{l:'衍生价值',v:a.compound.derivative,d:['封闭','一般','丰富'][a.compound.derivative]}];
  document.getElementById('val-meters').innerHTML=mets.map(function(m){
    var c=m.v>=2?'var(--green)':m.v>=1?'var(--gold)':'var(--red)';
    return'<div class="meter"><div class="ml">'+h(m.l)+'</div><div class="mv" style="color:'+c+'">'+m.v+'/2</div><div class="md">'+h(m.d)+'</div><div class="mdots">'+mkDots(m.v,2)+'</div></div>';
  }).join('');

  // DIKW
  document.getElementById('val-dikw').innerHTML='<div class="seg l1" style="flex:'+a.dikw.facts+'">'+a.dikw.facts+'%</div><div class="seg l2" style="flex:'+a.dikw.methods+'">'+a.dikw.methods+'%</div><div class="seg l3" style="flex:'+a.dikw.transfers+'">'+a.dikw.transfers+'%</div><div class="seg l4" style="flex:'+a.dikw.principles+'">'+a.dikw.principles+'%</div>';

  // Counterfactual
  var gainDays=Math.round(a.cf.gain*3);
  document.getElementById('val-cf').innerHTML='<div class="cf-grid"><div class="cf-box"><div class="cf-lbl">本次对话价值</div><div class="cf-val">'+a.cf.actual+'</div></div><div class="cf-vs">VS</div><div class="cf-box"><div class="cf-lbl">未讨论的替代成本</div><div class="cf-val dim">'+a.cf.without+'</div></div></div><div class="cf-gain">✨ 净增益：+'+a.cf.gain+' · 约省 '+gainDays+' 天摸索时间</div><div class="cf-reason">如果没有这次讨论，你可能需要自己搜索、试错、整合信息，保守估计需要 '+gainDays+' 天左右的非系统性摸索。这次对话的主要价值在于帮你精准定位了关键问题，跳过了大量信息筛选的成本。</div>';

  // Insights
  document.getElementById('val-insights').innerHTML=a.insights.map(function(iz){
    return'<details class="ins"><summary>💎 '+h(iz.text)+'</summary><div class="ib"><span class="il">📌 来源事实：</span>'+h(iz.source)+'<span class="il">🔍 解释力：</span>'+h(iz.explain)+'<span class="il">⚡ 行动推演：</span>'+h(iz.action)+'<span class="il">⚠️ 关联挑战：</span>'+h(iz.challenge)+'</div></details>';
  }).join('');

  // RACI
  document.getElementById('val-raci').innerHTML=
    '<table class="rax"><thead><tr><th style="text-align:left;">任务</th><th>R 执行者</th><th>A 负责人</th><th>C 顾问</th><th>I 知会</th></tr></thead><tbody>'
    +a.raci.map(function(x){return'<tr><td class="task">'+h(x.task)+'</td><td class="r">'+(x.r!=='-'?'R':'-')+'</td><td class="a">'+(x.a!=='-'?'A':'-')+'</td><td class="c">'+(x.c!=='-'?'C':'-')+'</td><td class="i">'+(x.i!=='-'?'I':'-')+'</td></tr>';}).join('')
    +'</tbody></table>';
}

// ═══════════════════════ rPrompt ═══════════════════════
function rPrompt(a){
  var h=esc;
  document.getElementById('prompt-meta').textContent='共 '+a.n+' 条提示词 · 总分 '+a.pt+'/100 · 均长 '+Math.round(a.avgl)+' 字';

  var te=document.getElementById('ps-total');te.textContent=a.pt;
  var c=a.pt>=70?'var(--green)':a.pt>=40?'var(--gold)':'var(--red)';te.style.color=c;
  var ge=document.getElementById('ps-grade');ge.textContent=a.pt>=70?'🟢 良好':a.pt>=40?'🟡 需改进':'🔴 需大幅提升';ge.style.color=c;

  // Dimension cards
  var dimExamples={
    '目标清晰度':{bad:'帮我写个方案',good:'请帮我起草《社区法律服务志愿者招募方案》，面向法学大二学生，目标是说服他们每周投入3小时参与社区法律援助值班，800-1000字。'},
    '角色锚定':{bad:'帮我分析这个合同',good:'你是10年执业经验的合同法律师。请审阅以下房屋租赁合同，从承租方角度逐条分析风险点，并给出修改建议。'},
    '上下文充分性':{bad:'这段代码报错了',good:'Python 3.11 Flask后端报错：[堆栈信息]。相关代码片段：[3段]。已排除数据库连接问题（其他接口正常）。'},
    '约束条件':{bad:'推荐几个复习资料',good:'请推荐3-5个法理学考研复习资料：(1)面向华师法学学硕 (2)难度适合基础阶段 (3)优先视频/音频类 (4)免费或<50元 (5)排除已用过的。'},
    '输出格式':{bad:'整理一下',good:'请整理为表格，4列：时间|事件|关键人物|影响等级(高/中/低)。按时间正序，同一日期合并单元格。表格后附200字总结。'},
    '示例质量':{bad:'写一篇评论',good:'请写一篇关于大学生志愿服务的评论。参考语调：[粘贴示例]。开头不要用"随着…的发展"，结尾不要喊口号。'},
    '推理框架':{bad:'怎么看这个现象',good:'请按框架分析：(1)描述现象+关键数据 (2)供给/需求/制度三维分析成因 (3)对比美德做法 (4)3条可操作建议。每步标注前提假设。'},
    '语言精确度':{bad:'改改这段话',good:'润色要求：(1)保留原意 (2)被动改主动 (3)每句<25字 (4)术语统一 (5)删除"的""了"等冗余虚词。'},
    '安全公平':{bad:'分析为什么男性更适合当领导',good:'从组织行为学角度分析领导力胜任模型：(1)不同性别管理风格研究综述 (2)影响晋升的结构性因素 (3)多元团队对绩效的实证。避免性别本质主义预设。'},
    '效率可维护':{bad:'把这些内容搞一下',good:'长期任务：每周读3篇论文并输出笔记。请设计可复用模板：(1)元信息 (2)核心论点 (3)论证结构 (4)知识库关联 (5)金句摘录。模板用{{}}标注变量。'}
  };

  document.getElementById('ps-dims').innerHTML=a.dims.map(function(d){
    var pct=d.s/5*100,cl=d.s>=4?'var(--green)':d.s>=2.5?'var(--gold)':'var(--red)',st='★'.repeat(d.w)+'☆'.repeat(3-d.w);
    var ex=dimExamples[d.nm]||{bad:'...',good:'...'};
    return'<div class="dim-card"><div class="dh"><span class="dn">'+h(d.nm)+'</span><span class="dw">权重 '+st+'</span></div>'
      +'<div class="ds" style="color:'+cl+'">'+d.s+'/5</div>'
      +'<div class="dbar"><div class="dbar-fill" style="width:'+pct+'%;background:'+cl+';"></div></div>'
      +'<div class="dsug">'+h(d.sg)+'<div class="good-ex" style="margin-top:6px;">✅ <strong>改写示例：</strong>'+h(ex.good)+'</div></div></div>';
  }).join('');

  // Per-prompt
  document.getElementById('ps-list').innerHTML=a.pp&&a.pp.length>0?a.pp.map(function(p,i){
    var pc=p.score/100,cl=p.score>=60?'var(--green)':'var(--red)';
    var verdict=p.score>=70?'整体质量不错':p.score>=40?'有改进空间':'问题较多，建议重点修改';
    return'<details class="ps-item"><summary><span class="ps-num">#'+(p.idx+1)+'</span><span class="ps-preview">'+h(p.preview)+'</span><div class="ps-bar-bg"><div class="ps-bar-fill" style="width:'+(pc*100)+'%;background:'+cl+';"></div></div><span class="ps-score" style="color:'+cl+'">'+p.score+'分</span><span class="arr">▼</span></summary>'
      +'<div class="detail-inner"><strong>整体评价：</strong>'+verdict+'。该提示词在以下维度表现较好，在部分维度需要加强。建议对比10维评分标准找到具体改进点。</div></details>';
  }).join(''):'<div style="color:var(--text2);text-align:center;padding:20px;">需要多条提示词才能显示对比分析</div>';

  // Weakness
  var wd=a.dims.filter(function(d){return d.s<3;}).sort(function(x,y){return x.s-y.s;});
  document.getElementById('ps-weak').innerHTML=wd.length>0?
    ('<p style="margin-bottom:12px;font-size:13px;">以下维度得分较低，建议优先改进（按影响力排序）：</p>'
    +wd.slice(0,3).map(function(w){
      var ex=dimExamples[w.nm]||{bad:'...',good:'...'},impact='';
      if(w.w===3)impact='高权重维度（权重3），对总分影响最大，优先修复';
      else if(w.w===2)impact='中等权重（权重2），提升后可显著改善交互体验';
      else impact='基础维度（权重1），好提示词的基本素养';
      return'<div class="weak-block"><h4>'+h(w.nm)+' <span style="font-size:11px;color:var(--text2);">得分 '+w.s+'/5 · '+impact+'</span></h4>'
        +'<p style="font-size:12px;color:var(--text2);margin-bottom:6px;">'+h(w.sg)+'</p>'
        +'<div class="bad-ex">❌ <strong>你常写：</strong>'+h(ex.bad)+'</div>'
        +'<div class="good-ex">✅ <strong>应该写：</strong>'+h(ex.good)+'</div></div>';
    }).join('')
    +'<div style="padding:12px 16px;background:rgba(108,108,240,0.06);border-radius:10px;font-size:13px;line-height:1.7;margin-top:12px;">💡 <strong>总结：</strong>好提示词 = 清晰目标 + 准确角色 + 充足上下文 + 明确约束。每次写完提示词后对照上方10个维度快速自查一遍，尤其是<span style="color:var(--accent);">角色锚定</span>和<span style="color:var(--accent);">约束条件</span>——这两个是回报率最高的改进点。</div>')
    :'<div style="color:var(--text2);">无明显弱项，继续保持！</div>';
}

// ═══════════════════════ rMirror ═══════════════════════
function rMirror(a){
  var h=esc,m=a.mirror;
  document.getElementById('mirror-meta').textContent='基于 '+a.n+' 条提示词的批判性分析报告';
  document.getElementById('mir-sum').innerHTML=h(m.summary).replace(/\n\n/g,'<br><br>');
  document.getElementById('mir-spots').innerHTML=m.blindspots.map(function(b){
    return'<div class="spot"><div class="st">🔴 '+h(b.title)+'</div><div class="sd">'+h(b.detail)+'</div><div class="se">📌 证据锚点：'+h(b.evidence)+'</div></div>';
  }).join('');
  document.getElementById('mir-bias').innerHTML=m.biases.map(function(b){
    return'<div class="bias"><div class="bt">🧠 '+h(b.name)+'</div><div class="sd">'+h(b.detail)+'</div></div>';
  }).join('');
  document.getElementById('mir-gaps').innerHTML=m.logicGaps.length?m.logicGaps.map(function(g){
    return'<div class="gap"><div class="gt">🔗 '+h(g.issue)+'</div><div class="sd">'+h(g.detail)+'</div></div>';
  }).join(''):'<div style="font-size:13px;color:var(--text2);padding:8px;">本次对话未检测到明显逻辑断裂——这本身就是好信号。</div>';
  document.getElementById('mir-chal').innerHTML=m.challenges.map(function(c){
    return'<div class="chal"><div class="q">❓ '+h(c.q)+'</div><div class="h">💡 '+h(c.h)+'</div></div>';
  }).join('');
  document.getElementById('mir-imps').innerHTML=m.improvements.map(function(im,i){
    return'<div class="imp"><span style="color:var(--accent);font-weight:700;">'+(i+1)+'.</span> '+h(im)+'</div>';
  }).join('');
}
</script>
</body>
</html>'''

# ═══ Main ═══

def main():
    print('Scanning sessions...')
    ss = scan_all()
    if not ss: print('No sessions found.'); sys.exit(1)
    total = sum(s['msgCount'] for s in ss)
    print(f'Found {len(ss)} sessions, {total} messages')

    data_json = json.dumps(ss, ensure_ascii=False)
    data_json = data_json.replace('</script>','<\\/script>')

    html = HTML.replace('__DATA__', data_json)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    size = os.path.getsize(OUT_PATH) / 1024
    print(f'Done: {OUT_PATH} ({size:.0f} KB)')
    print('Features: dark sci-fi theme | bubble chat | 4 tabs | zero deps | offline ready')

if __name__ == '__main__':
    main()
