# generate_index.py - Unified Index Generator for HV Analysis
import json, os, urllib.parse

INDEX_FILE = '/root/projects/hv-reports/index.html'
DATA_FILE = '/root/projects/hv-reports/search-index.json'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    reports = json.load(f)

# Total stats
total_reports = len(reports)
total_words = sum(r.get('char_count', 0) for r in reports)
total_words_k = f"{round(total_words / 1000, 1)}k"
categories = sorted(list(set(r['category'] for r in reports if r['category'] != '方法论')))

featured = next((r for r in reports if r['slug'] == 'welcome'), reports[0])
standard_reports = [r for r in reports if r['slug'] != 'welcome']

def build_card(r):
    url = f"reports/{urllib.parse.quote(r.get('file', r['slug'] + '.html'))}"
    tags_html = "".join([f'<span class="card-tag">#{t}</span>' for t in r.get('tags', [])[:2]])
    desc = r.get('desc', '')
    if len(desc) > 130:
        desc = desc[:130] + '...'
    read_time = r.get('read_time', '8 min')

    return f'''
    <a href="{url}" class="report-card" data-category="{r.get('category', '')}" data-tags="{','.join(r.get('tags', []))}">
      <div class="card-meta">
        <span class="card-cat-badge">{r.get('category', '深度研报')}</span>
        <span class="card-read-time">⏱ {read_time}</span>
      </div>
      <h3 class="card-title">{r.get('title', '')}</h3>
      <p class="card-desc">{desc}</p>
      <div class="card-footer">
        <div class="card-tags-group">{tags_html}</div>
        <span class="card-link-arrow">阅读研报 →</span>
      </div>
    </a>
    '''

cards_html = "\n".join([build_card(r) for r in standard_reports])
featured_url = f"reports/{urllib.parse.quote(featured.get('file', featured['slug'] + '.html'))}"

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HV Analysis | 横纵分析法深度商业与科技研究智库</title>
  <meta name="description" content="横纵分析法 (HV Analysis) 智库——以横向竞品矩阵为经、纵向产业演进为纬，系统透视商业与科技底层机理。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/theme.css?v=20260909">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/fuse.js/6.6.2/fuse.basic.min.js"></script>
  <style>
    /* Specific Home Hero & Cards Styles */
    .hero-section {{
      padding: 4.5rem 1.5rem 3rem;
      max-width: 1100px;
      margin: 0 auto;
      text-align: center;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 0.95rem;
      background: var(--primary-light);
      border: 1px solid var(--primary-glow);
      color: var(--primary);
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      margin-bottom: 1.5rem;
    }}
    .hero-title {{
      font-size: clamp(2.2rem, 5vw, 3.4rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      color: var(--navy);
      line-height: 1.18;
      margin-bottom: 1.25rem;
    }}
    .gradient-text {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent-cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
      font-size: clamp(1rem, 2vw, 1.15rem);
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 2.2rem;
      line-height: 1.7;
    }}
    
    /* Stats Bar */
    .stats-container {{
      display: inline-flex;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 0.75rem 1.8rem;
      box-shadow: var(--shadow-sm);
      gap: 2.2rem;
      margin-bottom: 3.5rem;
    }}
    .stat-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .stat-num {{
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--navy);
      font-family: var(--font-mono);
    }}
    .stat-label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    /* Featured Methodology Banner */
    .featured-section {{
      max-width: 1280px;
      margin: 0 auto 3.5rem;
      padding: 0 1.5rem;
    }}
    .featured-card {{
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%), var(--bg-card);
      border: 1px solid rgba(37, 99, 235, 0.2);
      border-radius: var(--radius-xl);
      padding: 2.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 2.5rem;
      box-shadow: var(--shadow-md);
      transition: all 0.25s ease;
      text-decoration: none;
      color: inherit;
    }}
    .featured-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-xl);
      border-color: var(--primary);
    }}
    .featured-tag {{
      display: inline-block;
      background: var(--primary);
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      margin-bottom: 0.75rem;
    }}
    .featured-title {{
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--navy);
      margin-bottom: 0.75rem;
    }}
    .featured-desc {{
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.6;
      max-width: 780px;
    }}
    .featured-action {{
      background: var(--primary);
      color: #fff;
      padding: 0.75rem 1.5rem;
      border-radius: var(--radius-md);
      font-weight: 700;
      font-size: 0.9rem;
      white-space: nowrap;
      transition: background 0.15s;
    }}
    .featured-card:hover .featured-action {{
      background: var(--primary-hover);
    }}

    /* Controls Bar */
    .portal-main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 1.5rem 5rem;
    }}
    .controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.25rem;
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--border);
    }}
    .filter-pills {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .filter-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 0.95rem;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }}
    .filter-btn:hover {{
      border-color: var(--primary);
      color: var(--text-main);
    }}
    .filter-btn.active {{
      background: var(--navy);
      color: #ffffff;
      border-color: var(--navy);
    }}
    [data-theme="dark"] .filter-btn.active {{
      background: var(--primary);
      border-color: var(--primary);
      color: #fff;
    }}
    .view-toggles {{
      display: flex;
      align-items: center;
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 2px;
    }}
    .view-btn {{
      background: transparent;
      border: none;
      padding: 0.35rem 0.65rem;
      border-radius: 4px;
      color: var(--text-muted);
      font-size: 0.8rem;
      cursor: pointer;
      font-weight: 600;
    }}
    .view-btn.active {{
      background: var(--bg-card);
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
    }}

    /* Reports Grid */
    .reports-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.5rem;
    }}
    .reports-grid.list-mode {{
      grid-template-columns: 1fr;
    }}
    .report-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 1.6rem;
      display: flex;
      flex-direction: column;
      text-decoration: none;
      color: inherit;
      box-shadow: var(--shadow-card);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }}
    .report-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-lg);
      border-color: rgba(37, 99, 235, 0.35);
    }}
    .card-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.85rem;
    }}
    .card-cat-badge {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--primary);
      background: var(--primary-light);
      padding: 2px 8px;
      border-radius: 4px;
    }}
    .card-read-time {{
      font-size: 0.75rem;
      color: var(--text-subtle);
    }}
    .card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--navy);
      line-height: 1.4;
      margin-bottom: 0.65rem;
    }}
    .card-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 1.25rem;
      flex: 1;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 0.95rem;
      border-top: 1px solid var(--border-subtle);
    }}
    .card-tag {{
      font-size: 0.72rem;
      color: var(--text-subtle);
      margin-right: 0.4rem;
    }}
    .card-link-arrow {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--primary);
      transition: transform 0.15s;
    }}
    .report-card:hover .card-link-arrow {{
      transform: translateX(3px);
    }}

    /* Site Footer */
    .site-footer {{
      border-top: 1px solid var(--border);
      padding: 3.5rem 1.5rem 2.5rem;
      background: var(--bg-card);
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    @media (max-width: 768px) {{
      .featured-card {{ flex-direction: column; align-items: flex-start; gap: 1.5rem; }}
      .reports-grid {{ grid-template-columns: 1fr; }}
      .stats-container {{ gap: 1.2rem; padding: 0.6rem 1.2rem; }}
    }}
  </style>
</head>
<body data-root="./">

  <!-- Unified Site Header -->
  <header class="site-header">
    <div class="site-header-inner">
      <a href="./" class="site-brand">
        <div class="site-brand-symbol">HV</div>
        <div>
          <span class="site-brand-text">HV Analysis</span>
          <span class="site-brand-sub">研究智库</span>
        </div>
      </a>
      <div class="site-nav-group">
        <button class="search-trigger-btn cmd-search-trigger" title="搜索研报 (Cmd + K)">
          <span>🔍 全站检索</span>
          <kbd>⌘K</kbd>
        </button>
        <a href="reports/welcome.html" class="nav-link">方法论</a>
        <a href="https://github.com/KrisAlthea/hv-reports" target="_blank" class="btn-github-link">
          <span>GitHub</span>
          <span>↗</span>
        </a>
        <button class="btn-icon-action theme-toggle-btn" aria-label="切换深浅色主题">🌓</button>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero-section">
    <div class="hero-badge">
      <span>●</span>
      <span>横纵分析法 · 产业与商业研究智库</span>
    </div>
    <h1 class="hero-title">
      以经纬之维，<span class="gradient-text">透视产业与底层机理</span>
    </h1>
    <p class="hero-subtitle">
      横向竞品矩阵（竞争边界与要素对撞）与纵向产业链（演进脉络与利润流转）交汇。基于前沿数据与微观机理的自动化研究门户。
    </p>

    <div class="stats-container">
      <div class="stat-item">
        <span class="stat-num">{total_reports}</span>
        <span class="stat-label">收录研报</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{len(categories)}</span>
        <span class="stat-label">核心赛道</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{total_words_k}</span>
        <span class="stat-label">分析字数</span>
      </div>
    </div>
  </section>

  <!-- Featured Methodology Spotlight -->
  <section class="featured-section">
    <a href="{featured_url}" class="featured-card">
      <div>
        <span class="featured-tag">智库学术支柱 · 旗舰方法论</span>
        <h2 class="featured-title">{featured.get('title')}</h2>
        <p class="featured-desc">{featured.get('desc')}</p>
      </div>
      <div class="featured-action">
        阅读方法论范式 →
      </div>
    </a>
  </section>

  <!-- Main Reports Directory -->
  <main class="portal-main">
    <div class="controls-bar">
      <div class="filter-pills" id="filterPills">
        <button class="filter-btn active" data-category="ALL">全部深度研报 ({total_reports - 1})</button>
        <button class="filter-btn" data-category="宏观与金融">宏观与金融</button>
        <button class="filter-btn" data-category="AI与科技">AI与科技</button>
        <button class="filter-btn" data-category="商业与消费">商业与消费</button>
        <button class="filter-btn" data-category="产业与制造">产业与制造</button>
      </div>
      <div class="view-toggles">
        <button class="view-btn active" id="gridModeBtn" title="网格视图">⊞ 网格</button>
        <button class="view-btn" id="listModeBtn" title="列表视图">☰ 列表</button>
      </div>
    </div>

    <div class="reports-grid" id="reportsGrid">
      {cards_html}
    </div>
  </main>

  <footer class="site-footer">
    <p>© 2026 HV Analysis Research Portal · 由 WeiHaoran 与 AI 协同研撰</p>
    <p style="font-size:0.75rem; margin-top:0.4rem; color:var(--text-subtle);">自动化研报编译体系 · Cloudflare Pages 全球高速托管</p>
  </footer>

  <!-- Universal Core JS -->
  <script src="assets/js/core.js?v=20260909"></script>
  <script>
    // Local Index Page Controls
    document.addEventListener('DOMContentLoaded', () => {{
      const filterPills = document.getElementById('filterPills');
      const cards = document.querySelectorAll('.report-card');
      const grid = document.getElementById('reportsGrid');
      const gridBtn = document.getElementById('gridModeBtn');
      const listBtn = document.getElementById('listModeBtn');

      // Category Filtering
      filterPills.addEventListener('click', (e) => {{
        const btn = e.target.closest('.filter-btn');
        if (!btn) return;
        filterPills.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const cat = btn.getAttribute('data-category');
        cards.forEach(card => {{
          if (cat === 'ALL' || card.getAttribute('data-category') === cat) {{
            card.style.display = '';
          }} else {{
            card.style.display = 'none';
          }}
        }});
      }});

      // View Mode Toggle
      gridBtn.addEventListener('click', () => {{
        grid.classList.remove('list-mode');
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
      }});

      listBtn.addEventListener('click', () => {{
        grid.classList.add('list-mode');
        listBtn.classList.add('active');
        gridBtn.classList.remove('active');
      }});
    }});
  </script>
</body>
</html>
'''

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated unified index.html successfully.")
