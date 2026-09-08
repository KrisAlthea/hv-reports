import json, os, glob, re
from bs4 import BeautifulSoup

INDEX_HTML_PATH = '/root/projects/hv-reports/index.html'
SEARCH_INDEX_PATH = '/root/projects/hv-reports/search-index.json'

with open(SEARCH_INDEX_PATH, 'r', encoding='utf-8') as f:
    reports_data = json.load(f)

# Build Cards HTML
cards_html_list = []
for r in reports_data:
    card = f'''        <a href="{r['url']}" class="report-card" data-category="{r['cat']}" data-tag="{r['tag']}">
          <div class="card-meta">
            <span class="card-tag">{r['icon']} {r['tag']}</span>
            <div class="card-meta-right">
              <span class="card-read-time">⏱️ {r['min']} min</span>
              <span class="card-date">{r['date']}</span>
            </div>
          </div>
          <h3 class="card-title">{r['title']}</h3>
          <p class="card-desc">{r['summary'][:130]}...</p>
          <div class="card-footer">
            <span class="card-author">✍️ WeiHaoran</span>
            <span class="card-action">查阅研报 →</span>
          </div>
        </a>'''
    cards_html_list.append(card)

cards_html = '\n\n'.join(cards_html_list)

full_html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HV Analysis | 横纵分析法深度研究智库</title>
  <meta name="description" content="基于历时-共时方法论与商业战略模型的深度产业与科技智库。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --font-sans: 'Plus Jakarta Sans', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      /* Light Theme (Mintlify/Stripe Warm Editorial) */
      --bg-base: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-elevated: #ffffff;
      --bg-subtle: #f1f5f9;
      --border: #e2e8f0;
      --border-focus: #3b82f6;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-faint: #94a3b8;
      
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-subtle: rgba(37, 99, 235, 0.08);
      
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.06), 0 2px 4px -2px rgba(0,0,0,0.04);
      --shadow-hover: 0 12px 24px -4px rgba(15, 23, 42, 0.08), 0 4px 8px -2px rgba(15, 23, 42, 0.04);
      --shadow-modal: 0 20px 25px -5px rgba(0,0,0,0.2), 0 8px 10px -6px rgba(0,0,0,0.1);

      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-full: 9999px;
      --header-blur: blur(12px);
    }}

    [data-theme="dark"] {{
      --bg-base: #090d16;
      --bg-surface: #0f172a;
      --bg-surface-elevated: #1e293b;
      --bg-subtle: #172033;
      --border: #1e293b;
      --border-focus: #60a5fa;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-faint: #64748b;
      
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-subtle: rgba(59, 130, 246, 0.15);
      
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.4);
      --shadow-hover: 0 12px 24px -4px rgba(0,0,0,0.5);
      --shadow-modal: 0 25px 50px -12px rgba(0,0,0,0.7);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-base);
      color: var(--text-main);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.25s ease, color 0.25s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Global Header */
    .site-header {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: var(--header-blur);
      -webkit-backdrop-filter: var(--header-blur);
      border-bottom: 1px solid var(--border);
      transition: background 0.25s ease, border-color 0.25s ease;
    }}

    [data-theme="dark"] .site-header {{
      background: rgba(15, 23, 42, 0.85);
    }}

    .nav-container {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: inherit;
    }}

    .brand-logo {{
      width: 34px;
      height: 34px;
      background: linear-gradient(135deg, #1e3a8a, var(--primary));
      color: white;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 14px;
      letter-spacing: -0.5px;
      box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }}

    .brand-title {{
      font-size: 17px;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }}

    .brand-tag {{
      font-size: 10px;
      font-weight: 700;
      color: var(--primary);
      background: var(--primary-subtle);
      padding: 2px 6px;
      border-radius: var(--radius-sm);
      margin-left: 6px;
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .nav-link {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 13.5px;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      transition: color 0.15s;
    }}

    .nav-link:hover {{
      color: var(--primary);
    }}

    .btn-theme-toggle {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border);
      background: var(--bg-surface);
      color: var(--text-muted);
      cursor: pointer;
      font-size: 16px;
      transition: all 0.2s;
    }}

    .btn-theme-toggle:hover {{
      border-color: var(--border-focus);
      color: var(--text-main);
    }}

    .btn-github {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--text-main);
      color: var(--bg-surface);
      padding: 7px 15px;
      border-radius: var(--radius-full);
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s;
    }}

    .btn-github:hover {{
      opacity: 0.9;
      transform: translateY(-1px);
    }}

    /* Hero Section */
    .hero {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 56px 24px 32px;
      text-align: center;
    }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-full);
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 20px;
      box-shadow: var(--shadow-sm);
    }}

    .hero-badge span {{
      color: var(--primary);
      font-weight: 700;
    }}

    .hero-title {{
      font-size: 42px;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.03em;
      line-height: 1.25;
      margin-bottom: 16px;
    }}

    .gradient-text {{
      background: linear-gradient(135deg, var(--primary) 0%, #06b6d4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero-desc {{
      font-size: 17px;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 32px;
      line-height: 1.6;
    }}

    /* Search & Filter Controls */
    .controls-wrapper {{
      max-width: 1280px;
      margin: 0 auto 36px;
      padding: 0 24px;
    }}

    .search-container {{
      position: relative;
      max-width: 580px;
      margin: 0 auto 20px;
    }}

    .search-input-box {{
      width: 100%;
      padding: 13px 90px 13px 44px;
      font-size: 14.5px;
      border: 1px solid var(--border);
      border-radius: var(--radius-full);
      background: var(--bg-surface);
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
      outline: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}

    .search-input-box:focus {{
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px var(--primary-subtle);
    }}

    .search-icon {{
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-faint);
      font-size: 16px;
    }}

    .kbd-shortcut {{
      position: absolute;
      right: 14px;
      top: 50%;
      transform: translateY(-50%);
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 3px 7px;
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-muted);
      font-weight: 600;
    }}

    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
    }}

    .filter-btn {{
      padding: 6px 15px;
      font-size: 13px;
      font-weight: 500;
      border-radius: var(--radius-full);
      border: 1px solid var(--border);
      background: var(--bg-surface);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .filter-btn:hover {{
      border-color: var(--border-focus);
      color: var(--text-main);
    }}

    .filter-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
      font-weight: 600;
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }}

    /* Reports Grid */
    .grid-container {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 24px 80px;
      flex: 1;
    }}

    .report-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
    }}

    .report-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 24px;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }}

    .report-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--primary), #06b6d4);
      opacity: 0;
      transition: opacity 0.25s ease;
    }}

    .report-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-hover);
      border-color: var(--border-focus);
    }}

    .report-card:hover::before {{
      opacity: 1;
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }}

    .card-meta-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-tag {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--primary);
      background: var(--primary-subtle);
      padding: 3px 9px;
      border-radius: var(--radius-full);
    }}

    .card-read-time {{
      font-size: 11.5px;
      color: var(--text-faint);
    }}

    .card-date {{
      font-size: 12px;
      color: var(--text-faint);
    }}

    .card-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.45;
      margin-bottom: 10px;
      letter-spacing: -0.01em;
      transition: color 0.15s;
    }}

    .report-card:hover .card-title {{
      color: var(--primary);
    }}

    .card-desc {{
      font-size: 13.5px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 20px;
      flex-grow: 1;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 14px;
      border-top: 1px solid var(--border);
      font-size: 12.5px;
    }}

    .card-author {{
      color: var(--text-muted);
      font-weight: 500;
    }}

    .card-action {{
      color: var(--primary);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: gap 0.2s;
    }}

    .report-card:hover .card-action {{
      gap: 7px;
    }}

    /* Global Cmd+K Search Modal */
    .search-modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(4px);
      z-index: 100;
      display: none;
      align-items: flex-start;
      justify-content: center;
      padding-top: 12vh;
      animation: fadeIn 0.15s ease-out;
    }}

    .search-modal-backdrop.open {{
      display: flex;
    }}

    .search-modal {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 640px;
      box-shadow: var(--shadow-modal);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      max-height: 70vh;
    }}

    .modal-header {{
      display: flex;
      align-items: center;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      gap: 12px;
    }}

    .modal-input {{
      flex: 1;
      font-size: 16px;
      border: none;
      outline: none;
      background: transparent;
      color: var(--text-main);
      font-family: inherit;
    }}

    .modal-close-btn {{
      background: var(--bg-subtle);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      padding: 3px 8px;
      font-size: 11px;
      font-family: var(--font-mono);
      cursor: pointer;
    }}

    .modal-results {{
      overflow-y: auto;
      padding: 8px 12px;
      flex: 1;
    }}

    .modal-result-item {{
      display: block;
      text-decoration: none;
      padding: 12px 14px;
      border-radius: var(--radius-md);
      color: inherit;
      transition: background 0.15s;
    }}

    .modal-result-item:hover, .modal-result-item.selected {{
      background: var(--primary-subtle);
    }}

    .modal-result-title {{
      font-size: 15px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 4px;
    }}

    .modal-result-snippet {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    .modal-result-snippet mark {{
      background: rgba(254, 240, 138, 0.6);
      color: inherit;
      padding: 1px 2px;
      border-radius: 2px;
    }}

    .modal-footer {{
      padding: 10px 18px;
      border-top: 1px solid var(--border);
      background: var(--bg-subtle);
      font-size: 12px;
      color: var(--text-faint);
      display: flex;
      justify-content: space-between;
    }}

    /* Footer */
    footer {{
      border-top: 1px solid var(--border);
      background: var(--bg-surface);
      padding: 36px 24px;
      text-align: center;
      color: var(--text-muted);
      font-size: 13.5px;
      margin-top: auto;
    }}

    @media (max-width: 768px) {{
      .hero-title {{ font-size: 30px; }}
      .hero-desc {{ font-size: 15px; }}
      .report-grid {{ grid-template-columns: 1fr; }}
      .nav-container {{ padding: 12px 16px; }}
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
  </style>
</head>
<body>
  <!-- Header -->
  <header class="site-header">
    <div class="nav-container">
      <a href="/" class="brand">
        <div class="brand-logo">HV</div>
        <div>
          <span class="brand-title">HV Analysis</span>
          <span class="brand-tag">RESEARCH</span>
        </div>
      </a>
      <div class="nav-actions">
        <button id="themeToggle" class="btn-theme-toggle" title="切换深色/浅色模式">🌓</button>
        <a href="reports/welcome.html" class="nav-link">关于方法论</a>
        <a href="https://github.com/KrisAlthea/hv-reports" target="_blank" class="btn-github">
          <span>GitHub</span>
          <span>↗</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-badge">
      <span>🚀 深度智库</span> 历时演进 · 共时格局 · 严谨研报
    </div>
    <h1 class="hero-title">
      透视底层逻辑，绘制<span class="gradient-text">商业与技术全景</span>
    </h1>
    <p class="hero-desc">
      融合历时-共时方法论与商学院战略模型，覆盖人工智能、金融宏观、消费文娱及高新技术的纵深研究。
    </p>
  </section>

  <!-- Controls: Search & Category Filters -->
  <div class="controls-wrapper">
    <div class="search-container">
      <span class="search-icon">🔍</span>
      <input type="text" id="quickSearchTrigger" class="search-input-box" placeholder="搜索研报主题、行业或全文段落..." readonly>
      <span class="kbd-shortcut">⌘ K</span>
    </div>
    <div class="filter-bar" id="filterBar">
      <button class="filter-btn active" data-filter="all">全部研报</button>
      <button class="filter-btn" data-filter="AI与科技">AI与科技</button>
      <button class="filter-btn" data-filter="宏观与金融">宏观与金融</button>
      <button class="filter-btn" data-filter="商业与消费">商业与消费</button>
      <button class="filter-btn" data-filter="产业与制造">产业与制造</button>
      <button class="filter-btn" data-filter="方法论">方法论</button>
    </div>
  </div>

  <!-- Reports Grid -->
  <main class="grid-container">
    <div class="report-grid" id="reportGrid">
{cards_html}
    </div>
  </main>

  <!-- Global Full-text Cmd+K Modal -->
  <div class="search-modal-backdrop" id="searchModal">
    <div class="search-modal">
      <div class="modal-header">
        <span style="font-size: 18px;">🔍</span>
        <input type="text" id="modalSearchInput" class="modal-input" placeholder="输入关键词全文搜索研报..." autocomplete="off">
        <button class="modal-close-btn" id="modalCloseBtn">ESC</button>
      </div>
      <div class="modal-results" id="modalResults">
        <div style="padding: 24px; text-align: center; color: var(--text-faint); font-size: 13.5px;">
          键入关键词进行全文深度匹配...
        </div>
      </div>
      <div class="modal-footer">
        <span>按 <strong>↑</strong> <strong>↓</strong> 选择，<strong>ENTER</strong> 访问</span>
        <span>HV Analysis Index</span>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer>
    <div>© 2026 HV Analysis Research. 保留所有权利。</div>
    <div style="margin-top: 6px; font-size: 12.5px; color: var(--text-faint);">
      架构：纯静态 Web HTML + 响应式双栏排版 · 部署于 Cloudflare Pages 全球边缘节点
    </div>
  </footer>

  <!-- Interactive Logic Script -->
  <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.js"></script>
  <script>
    // Theme Management (Light / Dark)
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    function initTheme() {{
      const savedTheme = localStorage.getItem('hv_theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      htmlEl.setAttribute('data-theme', savedTheme);
      updateThemeIcon(savedTheme);
    }}

    function updateThemeIcon(theme) {{
      themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }}

    themeToggle.addEventListener('click', () => {{
      const currentTheme = htmlEl.getAttribute('data-theme');
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', nextTheme);
      localStorage.setItem('hv_theme', nextTheme);
      updateThemeIcon(nextTheme);
    }});
    initTheme();

    // Instant Category Filter
    const filterBtns = document.querySelectorAll('.filter-btn');
    const reportCards = document.querySelectorAll('.report-card');

    filterBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;

        reportCards.forEach(card => {{
          if (filter === 'all' || card.dataset.category === filter || card.dataset.tag === filter) {{
            card.style.display = 'flex';
          }} else {{
            card.style.display = 'none';
          }}
        }});
      }});
    }});

    // Full-text Cmd+K Search Engine
    let searchData = [];
    let fuse = null;

    fetch('search-index.json')
      .then(res => res.json())
      .then(data => {{
        searchData = data;
        fuse = new Fuse(searchData, {{
          keys: [
            {{ name: 'title', weight: 0.6 }},
            {{ name: 'tag', weight: 0.2 }},
            {{ name: 'summary', weight: 0.2 }}
          ],
          threshold: 0.35,
          includeMatches: true
        }});
      }})
      .catch(err => console.error('Failed to load search index:', err));

    const searchModal = document.getElementById('searchModal');
    const quickTrigger = document.getElementById('quickSearchTrigger');
    const modalInput = document.getElementById('modalSearchInput');
    const modalResults = document.getElementById('modalResults');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    function openModal() {{
      searchModal.classList.add('open');
      modalInput.focus();
      modalInput.select();
    }}

    function closeModal() {{
      searchModal.classList.remove('open');
      modalInput.value = '';
      modalResults.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-faint); font-size: 13.5px;">键入关键词进行全文深度匹配...</div>';
    }}

    quickTrigger.addEventListener('click', openModal);
    modalCloseBtn.addEventListener('click', closeModal);
    searchModal.addEventListener('click', (e) => {{
      if (e.target === searchModal) closeModal();
    }});

    // Keyboard Shortcuts (Cmd+K / Ctrl+K / ESC)
    window.addEventListener('keydown', (e) => {{
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{
        e.preventDefault();
        openModal();
      }} else if (e.key === 'Escape' && searchModal.classList.contains('open')) {{
        closeModal();
      }}
    }});

    // Search Query Execution
    modalInput.addEventListener('input', (e) => {{
      const query = e.target.value.trim();
      if (!query || !fuse) {{
        modalResults.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-faint); font-size: 13.5px;">键入关键词进行全文深度匹配...</div>';
        return;
      }}

      const results = fuse.search(query).slice(0, 7);
      if (results.length === 0) {{
        modalResults.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-faint); font-size: 13.5px;">未找到匹配研报，换个关键词试试</div>';
        return;
      }}

      modalResults.innerHTML = results.map(res => {{
        const item = res.item;
        return `
          <a href="${{item.url}}" class="modal-result-item">
            <div style="font-size: 11px; font-weight: 600; color: var(--primary); margin-bottom: 2px;">${{item.icon}} ${{item.tag}} · ${{item.date}}</div>
            <div class="modal-result-title">${{item.title}}</div>
            <div class="modal-result-snippet">${{item.summary}}</div>
          </a>
        `;
      }}).join('');
    }});
  </script>
</body>
</html>
'''

with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Generated modern interactive index.html successfully!")
