import glob, os, re
from bs4 import BeautifulSoup

REPORTS_DIR = '/root/projects/hv-reports/reports'

HEAD_INJECTIONS = '''
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
'''

SCRIPT_INJECTION = '''
  <!-- Floating Reading Utilities & Interactive Logic -->
  <div class="reading-toolbar" id="readingToolbar">
    <button class="tool-btn" id="themeToggle" title="切换深色/浅色模式">🌓</button>
    <button class="tool-btn" id="copyShareBtn" title="复制研报链接与引用">📋</button>
    <button class="tool-btn" id="scrollToTopBtn" title="返回顶部">↑</button>
  </div>
  <div id="toast" class="toast-tip">已复制研报引用链接到剪贴板</div>

  <style>
    .reading-toolbar {
      position: fixed;
      right: 28px;
      bottom: 32px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 90;
    }
    .tool-btn {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      background: var(--bg-surface, #ffffff);
      border: 1px solid var(--border, #e2e8f0);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: var(--text-main, #0f172a);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .tool-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.12);
      border-color: #3b82f6;
    }
    .toast-tip {
      position: fixed;
      bottom: 84px;
      right: 28px;
      background: #0f172a;
      color: #ffffff;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      opacity: 0;
      pointer-events: none;
      transform: translateY(8px);
      transition: all 0.2s ease;
      z-index: 100;
    }
    .toast-tip.show {
      opacity: 1;
      transform: translateY(0);
    }
    .reading-progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, #2563eb, #06b6d4);
      z-index: 1000;
      width: 0%;
      transition: width 0.1s ease-out;
    }
    [data-theme="dark"] body {
      background-color: #090d16 !important;
      color: #f8fafc !important;
    }
    [data-theme="dark"] .article-container, 
    [data-theme="dark"] .report-body, 
    [data-theme="dark"] .report-content {
      background: transparent !important;
    }
    [data-theme="dark"] .site-header, 
    [data-theme="dark"] header {
      background: rgba(15, 23, 42, 0.85) !important;
      border-color: #1e293b !important;
    }
    [data-theme="dark"] .tool-btn {
      background: #1e293b;
      border-color: #334155;
      color: #f8fafc;
    }
    [data-theme="dark"] table {
      border-color: #1e293b;
    }
    [data-theme="dark"] th {
      background: #1e293b;
      color: #f8fafc;
    }
    [data-theme="dark"] td {
      border-color: #1e293b;
      color: #cbd5e1;
    }
    [data-theme="dark"] pre {
      background: #0d131f !important;
      border-color: #1e293b;
    }
  </style>

  <div class="reading-progress-bar" id="progressBar"></div>

  <script>
    // Theme Management
    const htmlEl = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');

    function applyTheme() {
      const savedTheme = localStorage.getItem('hv_theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      htmlEl.setAttribute('data-theme', savedTheme);
      if (themeToggle) {
        themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌓';
      }
    }

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const nextTheme = htmlEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        htmlEl.setAttribute('data-theme', nextTheme);
        localStorage.setItem('hv_theme', nextTheme);
        themeToggle.textContent = nextTheme === 'dark' ? '☀️' : '🌓';
      });
    }
    applyTheme();

    // Reading Progress Bar
    const progressBar = document.getElementById('progressBar');
    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      if (progressBar) progressBar.style.width = Math.min(100, Math.max(0, progress)) + '%';
    });

    // Scroll To Top
    const scrollBtn = document.getElementById('scrollToTopBtn');
    if (scrollBtn) {
      scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // Copy Quote & Share
    const copyBtn = document.getElementById('copyShareBtn');
    const toast = document.getElementById('toast');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const title = document.title || 'HV Analysis 研报';
        const url = window.location.href;
        const quote = `【${title}】\\n作者: WeiHaoran (HV Analysis)\\n链接: ${url}`;
        navigator.clipboard.writeText(quote).then(() => {
          if (toast) {
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
          }
        });
      });
    }

    // Mermaid Diagram Initializer
    document.addEventListener('DOMContentLoaded', () => {
      if (window.mermaid) {
        mermaid.initialize({
          startOnLoad: false,
          theme: htmlEl.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral',
          fontFamily: 'Plus Jakarta Sans, Noto Sans SC, sans-serif'
        });
        document.querySelectorAll('pre code.language-mermaid, pre code.mermaid').forEach((block) => {
          const pre = block.parentElement;
          const div = document.createElement('div');
          div.className = 'mermaid';
          div.textContent = block.textContent;
          pre.parentNode.replaceChild(div, pre);
        });
        mermaid.run();
      }

      // Dynamic Active TOC Observer (ScrollSpy)
      const headings = document.querySelectorAll('article h2, article h3, .report-body h2, .report-body h3');
      const tocLinks = document.querySelectorAll('.toc a, aside nav a');
      if (headings.length && tocLinks.length) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const id = entry.target.id;
              tocLinks.forEach(link => {
                if (link.getAttribute('href') === '#' + id) {
                  tocLinks.forEach(l => l.classList.remove('active'));
                  link.classList.add('active');
                }
              });
            }
          });
        }, { rootMargin: '0px 0px -75% 0px' });
        headings.forEach(h => observer.observe(h));
      }
    });
  </script>
'''

for p in glob.glob(os.path.join(REPORTS_DIR, '*.html')):
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove old toolbar/injections if any
    html = re.sub(r'<div class="reading-toolbar"[\s\S]*?<\/script>', '', html)
    
    # Inject CDN into head if missing
    if 'mermaid@10' not in html:
        html = html.replace('</head>', HEAD_INJECTIONS + '\n</head>')
        
    # Inject toolbar & JS before </body>
    html = html.replace('</body>', SCRIPT_INJECTION + '\n</body>')

    with open(p, 'w', encoding='utf-8') as f:
        f.write(html)

print("Injected modern interactive JS tools to all reports.")
