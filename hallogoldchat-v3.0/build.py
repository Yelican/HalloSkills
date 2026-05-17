#!/usr/bin/env python3
"""
HalloChatGold Board Builder v2.0
读取 ~/.claude/hallo-gold-chat/reports/ 的结构化 JSON 报告，
生成自包含的 HTML 看板。

用法：
  python build.py                          # 输出到桌面
  python build.py --serve                  # 启动本地预览服务器
  python build.py <输出路径>               # 指定输出路径

数据源：hallochatgold skill 自动存档的 JSON 报告
输出：自包含 HTML 文件，双击即可打开
"""

import json
import os
import sys
import glob
import datetime
import http.server
import socketserver

REPORTS_DIR = os.path.expanduser('~/.claude/hallo-gold-chat/reports')
DEFAULT_OUTPUT = os.path.expanduser('~/Desktop/HalloChatGold 看板.html')
PORT = 8899


def load_reports():
    """读取所有报告 JSON 文件，按时间降序排列"""
    reports = []
    if not os.path.isdir(REPORTS_DIR):
        print(f"[!] 报告目录不存在: {REPORTS_DIR}")
        return reports
    for fp in sorted(glob.glob(os.path.join(REPORTS_DIR, '*.json'))):
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'meta' not in data or 'kirkpatrick' not in data:
                print(f"[!] 跳过无效报告: {os.path.basename(fp)}")
                continue
            data['_file'] = os.path.basename(fp)
            reports.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[!] 读取失败 {os.path.basename(fp)}: {e}")
    reports.sort(key=lambda r: r.get('meta', {}).get('createdAt', ''), reverse=True)
    return reports


def compute_aggregate(reports):
    """计算聚合统计"""
    n = len(reports)
    if n == 0:
        return {'total': 0, 'avgScore': 0, 'maxScore': 0, 'minScore': 0,
                'scoreDistribution': {}, 'ratingDistribution': {}, 'byMonth': {}}
    scores = [r.get('kirkpatrick', {}).get('totalScore', 0) for r in reports]
    total_insights = sum(len(r.get('insights', [])) for r in reports)
    total_actions = sum(len(r.get('raci', [])) for r in reports)

    # 评分分布
    dist = {i: 0 for i in range(11)}
    for s in scores:
        dist[s] = dist.get(s, 0) + 1

    # 评级分布
    rating_dist = {'高价值 (8-10)': 0, '中等价值 (5-7)': 0, '低价值 (0-4)': 0}
    for s in scores:
        if s >= 8:
            rating_dist['高价值 (8-10)'] += 1
        elif s >= 5:
            rating_dist['中等价值 (5-7)'] += 1
        else:
            rating_dist['低价值 (0-4)'] += 1

    # 按月份统计
    by_month = {}
    for r in reports:
        month = r.get('meta', {}).get('createdAt', '')[:7]
        if month:
            by_month[month] = by_month.get(month, 0) + 1

    # S/A/B/C 评级分布
    compound_dist = {'S': 0, 'A': 0, 'B': 0, 'C': 0}
    for r in reports:
        c = r.get('compound', {}).get('rating', '')
        if c in compound_dist:
            compound_dist[c] += 1

    # 评分趋势（按时间升序，仅显示最近 N 个）
    sorted_by_time = sorted(reports, key=lambda r: r.get('meta', {}).get('createdAt', ''))
    score_trend = [{
        'title': r.get('meta', {}).get('title', ''),
        'score': r.get('kirkpatrick', {}).get('totalScore', 0),
        'date': r.get('meta', {}).get('createdAt', '')[:10]
    } for r in sorted_by_time]

    return {
        'total': n,
        'avgScore': round(sum(scores) / n, 1) if n else 0,
        'maxScore': max(scores) if scores else 0,
        'minScore': min(scores) if scores else 0,
        'totalInsights': total_insights,
        'totalActions': total_actions,
        'scoreDistribution': dist,
        'ratingDistribution': rating_dist,
        'compoundDistribution': compound_dist,
        'byMonth': by_month,
        'scoreTrend': score_trend
    }


def build_html(reports, aggregate):
    """生成完整的 HTML 页面，数据内嵌"""
    data_json = json.dumps(reports, ensure_ascii=False)
    agg_json = json.dumps(aggregate, ensure_ascii=False)
    data_json = data_json.replace('</script>', '<\\/script>').replace('</Script>', '<\\/Script>')
    agg_json = agg_json.replace('</script>', '<\\/script>').replace('</Script>', '<\\/Script>')

    html = HTML_TEMPLATE.replace('__DATA__', data_json)
    html = html.replace('__AGGREGATE__', agg_json)
    html = html.replace('__BUILD_TIME__', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    html = html.replace('__REPORT_COUNT__', str(len(reports)))
    return html


def build_all(output_path=None):
    """完整流程：加载 → 聚合 → 生成"""
    if output_path is None:
        output_path = DEFAULT_OUTPUT
    reports = load_reports()
    aggregate = compute_aggregate(reports)
    print(f"[+] 读取到 {len(reports)} 份报告")
    html = build_html(reports, aggregate)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"[+] 看板已生成: {output_path} ({size_kb:.0f} KB)")
    return output_path


def serve():
    """启动本地 HTTP 服务器预览"""
    output_path = build_all()
    www_dir = os.path.dirname(output_path) or '.'
    os.chdir(www_dir)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[+] 预览服务器启动: http://localhost:{PORT}")
        print(f"[+] 按 Ctrl+C 停止")
        httpd.serve_forever()


def main():
    if '--serve' in sys.argv:
        serve()
        return
    output = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else None
    build_all(output)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HalloChatGold 看板</title>
<style>
:root {
  --bg: #0f0f1a;
  --bg2: #16162a;
  --card: rgba(255,255,255,0.04);
  --card-hover: rgba(255,255,255,0.08);
  --border: rgba(255,255,255,0.08);
  --text: #e2e8f0;
  --text2: #94a3b8;
  --accent: #6366f1;
  --accent2: #818cf8;
  --green: #22c55e;
  --yellow: #eab308;
  --red: #ef4444;
  --radius: 12px;
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }

/* Layout */
.app { display: flex; height: 100vh; }

/* Sidebar */
.sidebar {
  width: 240px; flex-shrink: 0;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 20px 16px;
}
.logo {
  font-size: 20px; font-weight: 700;
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 28px;
}
.logo span { background: linear-gradient(135deg, var(--accent), #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.logo small { font-size: 12px; font-weight: 400; color: var(--text2); -webkit-text-fill-color: var(--text2); }
.nav { display: flex; flex-direction: column; gap: 4px; }
.nav-btn {
  background: transparent; border: none; color: var(--text2);
  padding: 10px 14px; border-radius: 8px; cursor: pointer;
  font-size: 14px; text-align: left; transition: all .15s;
  display: flex; align-items: center; gap: 10px;
}
.nav-btn:hover { background: rgba(255,255,255,0.05); color: var(--text); }
.nav-btn.active { background: rgba(99,102,241,0.15); color: var(--accent); font-weight: 600; }
.nav-icon { font-size: 16px; width: 20px; text-align: center; }

.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  font-size: 12px; color: var(--text2);
}

/* Main */
.main { flex: 1; overflow-y: auto; padding: 24px 32px; min-width: 0; }

/* Tabs */
.tab { display: none; }
.tab.active { display: block; }

/* Overview */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px; backdrop-filter: blur(8px);
}
.stat-card .label { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: .5px; }
.stat-card .value { font-size: 32px; font-weight: 700; margin-top: 4px; }
.stat-card .sub { font-size: 13px; color: var(--text2); margin-top: 2px; }

.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.chart-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px;
}
.chart-card h3 { font-size: 14px; font-weight: 600; margin-bottom: 16px; color: var(--text2); }

/* Score Trend */
.trend-chart { width: 100%; height: 120px; }
.trend-chart svg { width: 100%; height: 100%; }

/* Distribution bars */
.dist-bar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.dist-bar-label { font-size: 12px; width: 70px; flex-shrink: 0; color: var(--text2); }
.dist-bar-track { flex: 1; height: 20px; background: rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; }
.dist-bar-fill { height: 100%; border-radius: 10px; transition: width .6s ease; }
.dist-bar-count { font-size: 12px; width: 30px; text-align: right; color: var(--text2); }

/* Rating circles */
.rating-row { display: flex; gap: 12px; margin-top: 8px; }
.rating-item { flex: 1; text-align: center; }
.rating-item .circle { width: 40px; height: 40px; border-radius: 50%; margin: 0 auto 4px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; color: #fff; }
.rating-item .rlabel { font-size: 11px; color: var(--text2); }

/* Score trend dots */
.trend-dots { display: flex; align-items: flex-end; gap: 6px; height: 80px; padding: 8px 0; }
.trend-dot { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.trend-dot .bar { width: 100%; min-height: 2px; border-radius: 2px 2px 0 0; transition: height .3s; }
.trend-dot .dlabel { font-size: 10px; color: var(--text2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60px; text-align: center; }

/* Recent list */
.recent-list { display: flex; flex-direction: column; gap: 8px; }
.recent-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; transition: all .15s;
}
.recent-item:hover { background: var(--card-hover); border-color: var(--accent); }
.recent-item .ri-date { font-size: 12px; color: var(--text2); flex-shrink: 0; }
.recent-item .ri-title { flex: 1; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-item .ri-score {
  font-size: 13px; font-weight: 600; padding: 2px 10px; border-radius: 10px;
  flex-shrink: 0;
}

/* Timeline */
.timeline-layout { display: flex; gap: 20px; height: calc(100vh - 80px); }
.timeline-sidebar {
  width: 320px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 12px;
}
.tl-search {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 14px; color: var(--text); font-size: 14px;
  outline: none; width: 100%;
}
.tl-search::placeholder { color: var(--text2); }
.tl-search:focus { border-color: var(--accent); }
.tl-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.tl-filter {
  padding: 4px 12px; border-radius: 12px; font-size: 12px;
  border: 1px solid var(--border); background: transparent; color: var(--text2);
  cursor: pointer; transition: all .15s;
}
.tl-filter:hover { border-color: var(--text2); }
.tl-filter.active { background: rgba(99,102,241,0.2); border-color: var(--accent); color: var(--accent); }
.tl-list {
  flex: 1; overflow-y: auto;
  display: flex; flex-direction: column; gap: 6px;
}
.tl-item {
  padding: 10px 12px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; transition: all .15s;
}
.tl-item:hover { background: var(--card-hover); }
.tl-item.active { border-color: var(--accent); background: rgba(99,102,241,0.1); }
.tl-item .tli-title { font-size: 13px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tl-item .tli-meta { font-size: 11px; color: var(--text2); margin-top: 2px; display: flex; gap: 8px; }
.tl-item .tli-score {
  font-size: 12px; font-weight: 600; padding: 1px 8px; border-radius: 8px;
  display: inline-block;
}

/* Detail */
.timeline-detail {
  flex: 1; overflow-y: auto;
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 24px;
}
.detail-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; color: var(--text2); gap: 8px;
}
.detail-empty .big-icon { font-size: 48px; opacity: .3; }

.detail-header { margin-bottom: 24px; }
.detail-header h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.detail-header .dmeta { font-size: 13px; color: var(--text2); display: flex; gap: 16px; flex-wrap: wrap; }

.kp-section { margin-bottom: 24px; }
.kp-section h2 { font-size: 14px; font-weight: 600; color: var(--text2); margin-bottom: 12px; text-transform: uppercase; letter-spacing: .5px; }
.kp-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.kp-item { text-align: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; }
.kp-item .klabel { font-size: 11px; color: var(--text2); margin-bottom: 6px; }
.kp-dots { display: flex; justify-content: center; gap: 4px; }
.kp-dot {
  width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid var(--border); transition: all .2s;
}
.kp-dot.filled { border-color: var(--accent); background: var(--accent); box-shadow: 0 0 8px rgba(99,102,241,.4); }
.kp-total { text-align: center; margin-top: 10px; font-size: 18px; font-weight: 700; }
.kp-rating { font-size: 13px; color: var(--text2); }

/* DIKW bars */
.dikw-bar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.dikw-bar-label { font-size: 12px; width: 80px; flex-shrink: 0; color: var(--text2); }
.dikw-bar-track { flex: 1; height: 16px; background: rgba(255,255,255,0.06); border-radius: 8px; overflow: hidden; }
.dikw-bar-fill { height: 100%; border-radius: 8px; transition: width .6s; }
.dikw-bar-pct { font-size: 12px; width: 40px; text-align: right; color: var(--text2); }
.dikw-conclusion { font-size: 13px; color: var(--text2); margin-top: 8px; font-style: italic; }

/* Insights */
.insight-card {
  background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px; margin-bottom: 8px;
}
.insight-card h4 { font-size: 14px; margin-bottom: 8px; }
.insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.insight-field { }
.insight-field .if-label { font-size: 11px; color: var(--text2); margin-bottom: 2px; }
.insight-field .if-value { font-size: 13px; line-height: 1.4; }

.quote-block {
  border-left: 3px solid var(--accent); padding: 12px 16px; margin: 12px 0;
  background: rgba(99,102,241,0.06); border-radius: 0 8px 8px 0;
  font-style: italic; font-size: 13px; line-height: 1.6; color: var(--text2);
}

/* RACI table */
.raci-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.raci-table th { background: rgba(255,255,255,0.05); padding: 8px 12px; text-align: left; font-weight: 600; border-bottom: 1px solid var(--border); }
.raci-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
.raci-table .r-role { width: 30px; text-align: center; font-weight: 700; }
.raci-table .r-role.R { color: var(--accent); }
.raci-table .r-role.A { color: var(--green); }
.raci-table .r-role.C { color: var(--yellow); }
.raci-table .r-role.I { color: var(--text2); }

/* Counterfactual */
.cf-box { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.cf-item { background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; }
.cf-item .cfl { font-size: 11px; color: var(--text2); margin-bottom: 2px; }
.cf-item .cfv { font-size: 14px; font-weight: 600; }

/* Compound */
.compound-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.compound-item { text-align: center; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; }
.compound-item .cscore { font-size: 24px; font-weight: 700; }
.compound-item .clabel { font-size: 11px; color: var(--text2); margin: 2px 0; }
.compound-item .cdesc { font-size: 12px; color: var(--text2); }
.compound-rating {
  display: inline-block; padding: 4px 16px; border-radius: 16px;
  font-size: 14px; font-weight: 700; margin-top: 10px;
}

/* Full report */
.full-report {
  background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px; margin-top: 16px; max-height: 400px; overflow-y: auto;
  font-size: 13px; line-height: 1.6;
}
.full-report h1, .full-report h2 { font-size: 14px; font-weight: 700; margin: 12px 0 6px; }
.full-report table { width: 100%; border-collapse: collapse; font-size: 12px; margin: 8px 0; }
.full-report th, .full-report td { padding: 4px 8px; border: 1px solid var(--border); }
.full-report blockquote { border-left: 2px solid var(--accent); padding-left: 12px; margin: 8px 0; color: var(--text2); }
.full-report hr { border: none; border-top: 1px solid var(--border); margin: 12px 0; }

/* Score colors */
.score-high { color: var(--green); }
.score-mid { color: var(--yellow); }
.score-low { color: var(--red); }
.bg-high { background: rgba(34,197,94,0.2); color: var(--green); }
.bg-mid { background: rgba(234,179,8,0.2); color: var(--yellow); }
.bg-low { background: rgba(239,68,68,0.2); color: var(--red); }
.bg-none { background: rgba(255,255,255,0.05); color: var(--text2); }

/* About tab */
.about-content { max-width: 600px; line-height: 1.7; }
.about-content h2 { font-size: 18px; margin: 20px 0 8px; }
.about-content p { font-size: 14px; color: var(--text2); margin-bottom: 8px; }
.about-content code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.about-content ul { padding-left: 20px; font-size: 14px; color: var(--text2); }
.about-content li { margin-bottom: 4px; }

/* No data */
.no-data { text-align: center; padding: 60px 20px; color: var(--text2); }
.no-data h2 { font-size: 20px; margin-bottom: 8px; }
.no-data p { font-size: 14px; }

/* Empty state for detail */
.tl-empty-state { text-align: center; padding: 60px; color: var(--text2); }
.tl-empty-state .icon { font-size: 40px; margin-bottom: 8px; opacity: .3; }

/* Responsive */
@media (max-width: 900px) {
  .sidebar { width: 60px; padding: 16px 8px; }
  .sidebar .logo span, .sidebar .logo small, .sidebar .nav-btn span { display: none; }
  .sidebar-footer { display: none; }
  .nav-btn { justify-content: center; padding: 10px; }
  .nav-icon { margin: 0; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .timeline-layout { flex-direction: column; height: auto; }
  .timeline-sidebar { width: 100%; max-height: 200px; }
  .main { padding: 16px; }
  .kp-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
</head>
<body>
<div class="app">
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="logo">
      <span>HCG</span>
      <div><span>看板</span><small><br>__REPORT_COUNT__ 份报告</small></div>
    </div>
    <div class="nav">
      <button class="nav-btn active" data-tab="overview">
        <span class="nav-icon">📊</span><span>概览</span>
      </button>
      <button class="nav-btn" data-tab="timeline">
        <span class="nav-icon">📋</span><span>时间线</span>
      </button>
      <button class="nav-btn" data-tab="about">
        <span class="nav-icon">ℹ️</span><span>关于</span>
      </button>
    </div>
    <div class="sidebar-footer">
      v2.0 · 最后构建 __BUILD_TIME__
    </div>
  </div>

  <!-- Main Content -->
  <div class="main">
    <!-- Overview Tab -->
    <div class="tab active" id="tab-overview"></div>
    <!-- Timeline Tab -->
    <div class="tab" id="tab-timeline"></div>
    <!-- About Tab -->
    <div class="tab" id="tab-about">
      <div class="about-content">
        <h2>HalloChatGold 看板</h2>
        <p>这是你所有 <strong>对话淘金术</strong> 分析结果的聚合看板。</p>
        <p>每次你让凡哥复盘对话、提炼洞察，分析报告除了在对话中输出，还会自动存档到本地。跑一下 <code>python build.py</code> 就能把所有报告聚合到这里。</p>
        <h2>工作流</h2>
        <ul>
          <li>和 Claude 聊完 → 说「凡哥来个复盘」</li>
          <li>hallochatgold skill 执行完整 7 步管道 → 输出报告 + 自动存档</li>
          <li>跑 <code>python build.py</code> 更新看板</li>
          <li>双击桌面 HTML 文件，所有历史分析一目了然</li>
        </ul>
        <h2>数据存储</h2>
        <p>报告 JSON 文件保存在 <code>~/.claude/hallo-gold-chat/reports/</code></p>
        <p>所有分析由 Claude 在对话中实时生成（不是 Python 假数据）。</p>
        <h2>版本</h2>
        <p>v2.0 · 2026-05-17</p>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
const DATA = __DATA__;
const AGG  = __AGGREGATE__;

// ====== Utility ======
function scoreClass(s) {
  if (s >= 8) return 'score-high';
  if (s >= 5) return 'score-mid';
  return 'score-low';
}
function scoreBg(s) {
  if (s >= 8) return 'bg-high';
  if (s >= 5) return 'bg-mid';
  return 'bg-low';
}
function escHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ====== Tab Switching ======
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ====== Render Overview ======
function renderOverview() {
  const el = document.getElementById('tab-overview');
  if (DATA.length === 0) {
    el.innerHTML = '<div class="no-data"><h2>暂无报告</h2><p>运行 hallochatgold skill 生成第一份报告后，再跑 build.py 更新看板。</p></div>';
    return;
  }
  const a = AGG;
  let html = '';
  // Stats cards
  html += '<div class="stats-row">';
  html += `<div class="stat-card"><div class="label">总报告</div><div class="value">${a.total}</div></div>`;
  html += `<div class="stat-card"><div class="label">平均分</div><div class="value ${scoreClass(a.avgScore)}">${a.avgScore}<span style="font-size:14px">/10</span></div></div>`;
  html += `<div class="stat-card"><div class="label">总洞察</div><div class="value">${a.totalInsights}</div></div>`;
  html += `<div class="stat-card"><div class="label">总行动项</div><div class="value">${a.totalActions}</div></div>`;
  html += '</div>';

  // Charts row
  html += '<div class="charts-row">';

  // Score distribution
  html += '<div class="chart-card"><h3>评分分布</h3>';
  const dist = a.scoreDistribution;
  const maxDist = Math.max(1, ...Object.values(dist));
  for (let i = 10; i >= 0; i--) {
    const cnt = dist[i] || 0;
    const pct = (cnt / maxDist) * 100;
    const cls = scoreClass(i);
    html += `<div class="dist-bar-row">
      <div class="dist-bar-label">${i}分</div>
      <div class="dist-bar-track"><div class="dist-bar-fill" style="width:${pct}%;background:${i>=8?'var(--green)':i>=5?'var(--yellow)':'var(--red)'}"></div></div>
      <div class="dist-bar-count">${cnt}</div>
    </div>`;
  }
  html += '</div>';

  // Rating + Trend
  html += '<div class="chart-card"><h3>评级分布</h3>';
  const rd = a.ratingDistribution;
  const maxRd = Math.max(1, ...Object.values(rd));
  const rdColors = {'高价值 (8-10)': 'var(--green)', '中等价值 (5-7)': 'var(--yellow)', '低价值 (0-4)': 'var(--red)'};
  for (const [k, v] of Object.entries(rd)) {
    const pct = (v / maxRd) * 100;
    html += `<div class="dist-bar-row">
      <div class="dist-bar-label">${k}</div>
      <div class="dist-bar-track"><div class="dist-bar-fill" style="width:${pct}%;background:${rdColors[k]}"></div></div>
      <div class="dist-bar-count">${v}</div>
    </div>`;
  }

  // Compound rating distribution
  html += '<h3 style="margin-top:16px;">复利评级</h3>';
  const cd = a.compoundDistribution;
  const cdColors = {'S': '#a78bfa', 'A': 'var(--accent)', 'B': 'var(--yellow)', 'C': 'var(--red)'};
  const cdMax = Math.max(1, ...Object.values(cd));
  for (const [k, v] of Object.entries(cd)) {
    const pct = (v / cdMax) * 100;
    html += `<div class="dist-bar-row">
      <div class="dist-bar-label">${k}</div>
      <div class="dist-bar-track"><div class="dist-bar-fill" style="width:${pct}%;background:${cdColors[k]}"></div></div>
      <div class="dist-bar-count">${v}</div>
    </div>`;
  }
  html += '</div>';

  html += '</div>'; // end charts-row

  // Score Trend
  html += '<div class="chart-card" style="margin-bottom:24px;"><h3>评分趋势</h3>';
  const trend = a.scoreTrend || [];
  if (trend.length > 0) {
    const maxS = 10;
    html += '<div class="trend-dots">';
    trend.forEach(t => {
      const h = (t.score / maxS) * 100;
      html += `<div class="trend-dot">
        <div class="bar ${scoreClass(t.score)}" style="height:${Math.max(h,2)}%;background:${t.score>=8?'var(--green)':t.score>=5?'var(--yellow)':'var(--red)'}"></div>
        <div class="dlabel">${escHtml(t.date.slice(5))}</div>
      </div>`;
    });
    html += '</div>';
  } else {
    html += '<p style="color:var(--text2);font-size:13px;">暂无趋势数据</p>';
  }
  html += '</div>';

  // Recent reports
  html += '<div class="chart-card"><h3>最近分析</h3><div class="recent-list">';
  const recent = DATA.slice(0, 5);
  recent.forEach(r => {
    const m = r.meta;
    const ks = r.kirkpatrick;
    const d = (m.createdAt || '').slice(0, 10);
    html += `<div class="recent-item" onclick="switchToTimeline('${escHtml(m.id)}')">
      <div class="ri-date">${d}</div>
      <div class="ri-title">${escHtml(m.title)}</div>
      <div class="ri-score ${scoreBg(ks.totalScore)}">${ks.totalScore}/10</div>
    </div>`;
  });
  html += '</div></div>';

  el.innerHTML = html;
}

// ====== Render Timeline ======
let currentFilter = 'all';
let currentSearch = '';
let selectedId = null;

function getFilteredReports() {
  let list = DATA;
  if (currentFilter === 'high') list = list.filter(r => r.kirkpatrick.totalScore >= 8);
  else if (currentFilter === 'mid') list = list.filter(r => r.kirkpatrick.totalScore >= 5 && r.kirkpatrick.totalScore <= 7);
  else if (currentFilter === 'low') list = list.filter(r => r.kirkpatrick.totalScore < 5);
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    list = list.filter(r => (r.meta.title || '').toLowerCase().includes(q) ||
      JSON.stringify(r.insights || []).toLowerCase().includes(q));
  }
  return list;
}

function renderTimeline() {
  const el = document.getElementById('tab-timeline');
  const list = getFilteredReports();
  let html = '<div class="timeline-layout">';

  // Sidebar
  html += '<div class="timeline-sidebar">';
  html += `<input class="tl-search" type="text" placeholder="搜索报告标题或洞察..." value="${escHtml(currentSearch)}" oninput="onSearch(this.value)">`;
  html += '<div class="tl-filters">';
  const filters = [
    {key:'all', label:'全部'},
    {key:'high', label:'高分 8-10'},
    {key:'mid', label:'中等 5-7'},
    {key:'low', label:'低分 0-4'}
  ];
  filters.forEach(f => {
    html += `<button class="tl-filter${f.key===currentFilter?' active':''}" onclick="setFilter('${f.key}')">${f.label}</button>`;
  });
  html += '</div><div class="tl-list">';

  if (list.length === 0) {
    html += '<div style="padding:20px;text-align:center;color:var(--text2);font-size:13px;">没有匹配的报告</div>';
  } else {
    list.forEach(r => {
      const m = r.meta;
      const ks = r.kirkpatrick;
      const d = (m.createdAt || '').slice(0, 10);
      const active = m.id === selectedId ? ' active' : '';
      html += `<div class="tl-item${active}" onclick="selectReport('${escHtml(m.id)}')">
        <div class="tli-title">${escHtml(m.title)}</div>
        <div class="tli-meta">
          <span>${d}</span>
          <span>${escHtml(m.conversationType || '')}</span>
          <span class="tli-score ${scoreBg(ks.totalScore)}">${ks.totalScore}/10</span>
        </div>
      </div>`;
    });
  }

  html += '</div></div>'; // end tl-list, timeline-sidebar

  // Detail panel
  html += '<div class="timeline-detail" id="tl-detail">';
  if (selectedId) {
    const r = DATA.find(d => d.meta.id === selectedId);
    if (r) html += renderDetail(r);
    else html += '<div class="tl-empty-state"><div class="icon">🔍</div><p>报告未找到</p></div>';
  } else {
    html += '<div class="tl-empty-state"><div class="icon">📋</div><p>选择左侧一份报告查看详情</p></div>';
  }
  html += '</div></div>'; // end detail, timeline-layout
  el.innerHTML = html;
}

function renderDetail(r) {
  const m = r.meta, ks = r.kirkpatrick, d = r.dikw;
  let html = '';

  // Header
  html += `<div class="detail-header">
    <h1>${escHtml(m.title)}</h1>
    <div class="dmeta">
      <span>${(m.createdAt||'').slice(0,10)}</span>
      <span>${escHtml(m.conversationType||'')}</span>
      <span>${escHtml(m.participants||'')}</span>
    </div>
  </div>`;

  // Kirkpatrick
  html += '<div class="kp-section"><h2>Kirkpatrick 价值评分</h2><div class="kp-grid">';
  const levels = [
    {key:'reaction', label:'L1 反应'},
    {key:'learning', label:'L2 学习'},
    {key:'behavior', label:'L3 行为'},
    {key:'results', label:'L4 成果'},
    {key:'roi', label:'L5 ROI'}
  ];
  levels.forEach(lv => {
    const s = ks[lv.key] || {};
    const sc = s.score || 0;
    html += '<div class="kp-item">';
    html += `<div class="klabel">${lv.label}</div><div class="kp-dots">`;
    for (let i = 0; i < 3; i++) {
      html += `<div class="kp-dot${i < sc ? ' filled' : ''}"></div>`;
    }
    html += '</div></div>';
  });
  html += '</div>';
  html += `<div class="kp-total ${scoreClass(ks.totalScore)}">${ks.totalScore}/10</div>`;
  html += `<div class="kp-rating">${escHtml(ks.rating||'')}</div>`;
  html += '</div>';

  // DIKW
  html += '<div class="kp-section"><h2>内容分层 (DIKW)</h2>';
  const dikwColors = ['#a78bfa', '#6366f1', '#818cf8', '#4f46e5'];
  const dikwLabels = [
    {key:'L4_principles_pct', label:'L4 底层认知'},
    {key:'L3_transfers_pct', label:'L3 能力迁移'},
    {key:'L2_methods_pct', label:'L2 方法技能'},
    {key:'L1_facts_pct', label:'L1 事实信息'}
  ];
  dikwLabels.forEach((dl, i) => {
    const pct = d[dl.key] || 0;
    html += `<div class="dikw-bar-row">
      <div class="dikw-bar-label">${dl.label}</div>
      <div class="dikw-bar-track"><div class="dikw-bar-fill" style="width:${pct}%;background:${dikwColors[i]}"></div></div>
      <div class="dikw-bar-pct">${pct}%</div>
    </div>`;
  });
  if (d.conclusion) html += `<div class="dikw-conclusion">${escHtml(d.conclusion)}</div>`;
  html += '</div>';

  // Insights
  const insights = r.insights || [];
  if (insights.length > 0) {
    html += '<div class="kp-section"><h2>核心洞察</h2>';
    insights.forEach((ins, i) => {
      html += `<div class="insight-card">
        <h4>💎 洞察 ${i+1}：${escHtml(ins.title)}</h4>
        <div class="insight-grid">
          <div class="insight-field"><div class="if-label">来源事实</div><div class="if-value">${escHtml(ins.source)}</div></div>
          <div class="insight-field"><div class="if-label">解释力</div><div class="if-value">${escHtml(ins.explanatory)}</div></div>
          <div class="insight-field"><div class="if-label">行动推演</div><div class="if-value">${escHtml(ins.action)}</div></div>
          <div class="insight-field"><div class="if-label">关联挑战</div><div class="if-value">${escHtml(ins.challenge)}</div></div>
        </div>
      </div>`;
    });
    html += '</div>';
  }

  // Golden quote
  if (r.goldenQuote) {
    html += `<div class="quote-block">${escHtml(r.goldenQuote)}</div>`;
  }

  // RACI
  const raci = r.raci || [];
  if (raci.length > 0) {
    html += '<div class="kp-section"><h2>RACI 行动清单</h2><table class="raci-table"><thead><tr><th>角色</th><th>负责人</th><th>行动</th><th>截止时间</th></tr></thead><tbody>';
    raci.forEach(item => {
      html += `<tr>
        <td class="r-role ${item.role||''}">${escHtml(item.role||'')}</td>
        <td>${escHtml(item.actor||'')}</td>
        <td>${escHtml(item.action||'')}</td>
        <td>${escHtml(item.deadline||'')}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
  }

  // Counterfactual
  const cf = r.counterfactual || {};
  html += '<div class="kp-section"><h2>反事实价值</h2><div class="cf-box">';
  if (cf.withoutDiscussion) html += `<div class="cf-item"><div class="cfl">如果没有这次讨论</div><div class="cfv">${escHtml(cf.withoutDiscussion)}</div></div>`;
  if (cf.timeSaved) html += `<div class="cf-item"><div class="cfl">节省时间</div><div class="cfv">${escHtml(cf.timeSaved)}</div></div>`;
  if (cf.pitfallsAvoided) html += `<div class="cf-item"><div class="cfl">避免的坑</div><div class="cfv">${escHtml(cf.pitfallsAvoided)}</div></div>`;
  if (cf.valueEstimate) html += `<div class="cf-item"><div class="cfl">价值估算</div><div class="cfv">${escHtml(cf.valueEstimate)}</div></div>`;
  html += '</div></div>';

  // Compound
  const cp = r.compound || {};
  html += '<div class="kp-section"><h2>复利评估</h2><div class="compound-grid">';
  const cpItems = [
    {key:'leverage', label:'杠杆率'},
    {key:'halflife', label:'半衰期'},
    {key:'derivative', label:'衍生价值'}
  ];
  cpItems.forEach(ci => {
    const item = cp[ci.key] || {};
    html += `<div class="compound-item">
      <div class="cscore ${scoreClass(item.score||0)}">${item.score||0}</div>
      <div class="clabel">${ci.label}</div>
      <div class="cdesc">${escHtml(item.description||'')}</div>
    </div>`;
  });
  html += '</div>';
  if (cp.rating) {
    const rc = cp.rating === 'S' ? '#a78bfa' : cp.rating === 'A' ? 'var(--accent)' : cp.rating === 'B' ? 'var(--yellow)' : 'var(--red)';
    html += `<div class="compound-rating" style="background:${rc}22;color:${rc};border:1px solid ${rc}">复利评级：${cp.rating}</div>`;
  }
  html += '</div>';

  // Full report
  if (r.fullMarkdown) {
    html += '<div class="kp-section"><h2>完整报告</h2><div class="full-report">';
    const lines = r.fullMarkdown.split('\n');
    lines.forEach(line => {
      line = escHtml(line);
      if (line.startsWith('## ')) html += `<h2>${line.slice(3)}</h2>`;
      else if (line.startsWith('# ')) html += `<h1>${line.slice(2)}</h1>`;
      else if (line.startsWith('|')) {
        if (line.includes('---')) return;
        html += line + '\n';
      }
      else if (line.trim().startsWith('> ')) html += `<blockquote>${line.trim().slice(2)}</blockquote>`;
      else if (line.match(/^---+/)) html += '<hr>';
      else html += `<p>${line || '<br>'}</p>`;
    });
    html += '</div></div>';
  }

  return html;
}

// ====== Event Handlers ======
window.onSearch = function(v) {
  currentSearch = v;
  renderTimeline();
}

window.setFilter = function(f) {
  currentFilter = f;
  if (f === 'high' && selectedId) {
    const r = DATA.find(d => d.meta.id === selectedId);
    if (r && r.kirkpatrick.totalScore < 8) selectedId = null;
  } else if (f === 'mid' && selectedId) {
    const r = DATA.find(d => d.meta.id === selectedId);
    if (r && (r.kirkpatrick.totalScore < 5 || r.kirkpatrick.totalScore > 7)) selectedId = null;
  } else if (f === 'low' && selectedId) {
    const r = DATA.find(d => d.meta.id === selectedId);
    if (r && r.kirkpatrick.totalScore >= 5) selectedId = null;
  }
  renderTimeline();
}

window.selectReport = function(id) {
  selectedId = id;
  renderTimeline();
}

window.switchToTimeline = function(id) {
  selectedId = id;
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector('[data-tab="timeline"]').classList.add('active');
  document.getElementById('tab-timeline').classList.add('active');
  renderTimeline();
}

// ====== Init ======
renderOverview();
renderTimeline();

})();
</script>
</body>
</html>
"""


if __name__ == '__main__':
    main()
