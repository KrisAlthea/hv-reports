// /root/projects/hv-reports/assets/js/core.js
// Universal interactive brain for HV Analysis Research Portal & Reports

(function () {
  'use strict';

  // 1. Theme Manager (Synchronized across all pages via localStorage)
  const Theme = {
    key: 'hv_report_theme',
    init() {
      const saved = localStorage.getItem(this.key);
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const theme = saved || (prefersDark ? 'dark' : 'light');
      this.set(theme);

      // Listen for system theme changes if not overridden
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem(this.key)) {
          this.set(e.matches ? 'dark' : 'light');
        }
      });
    },
    set(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem(this.key, theme);
      document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
        btn.innerHTML = theme === 'dark' ? '☀️' : '🌓';
        btn.setAttribute('aria-label', `切换至${theme === 'dark' ? '浅色' : '深色'}模式`);
      });
      // Update mermaid theme if present
      if (window.mermaid) {
        document.querySelectorAll('.mermaid svg').forEach(svg => {
          // Re-render mermaid on theme change if needed
        });
      }
    },
    toggle() {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      this.set(current === 'dark' ? 'light' : 'dark');
    }
  };

  // 2. Global Toast Notification
  window.showToast = function (msg, duration = 2500) {
    let toast = document.querySelector('.global-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'global-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<span>✓</span><span>${msg}</span>`;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
  };

  // 3. Cmd+K Global Search Engine (Fuse.js powered)
  const Search = {
    fuse: null,
    data: [],
    isOpen: false,
    selectedIndex: -1,

    async init() {
      this.createModal();
      this.bindEvents();
      this.loadIndex();
    },

    async loadIndex() {
      try {
        const rootPath = document.body.getAttribute('data-root') || '';
        const res = await fetch(`${rootPath}search-index.json?v=${Date.now()}`);
        if (res.ok) {
          this.data = await res.json();
          if (window.Fuse) {
            this.fuse = new Fuse(this.data, {
              keys: ['title', 'tags', 'desc', 'category', 'slug'],
              threshold: 0.35,
              includeMatches: true
            });
          }
        }
      } catch (err) {
        console.warn('Search index load skipped or failed:', err);
      }
    },

    createModal() {
      if (document.querySelector('.cmd-modal-overlay')) return;
      const modal = document.createElement('div');
      modal.className = 'cmd-modal-overlay';
      modal.id = 'cmdSearchModal';
      modal.innerHTML = `
        <div class="cmd-modal-box">
          <div class="cmd-search-header">
            <span style="font-size:1.1rem; color:var(--text-muted);">🔍</span>
            <input type="text" class="cmd-search-input" id="cmdSearchInput" placeholder="输入关键词、行业、公司检索全站研报..." autocomplete="off">
            <kbd style="font-size:0.75rem; background:var(--bg-subtle); border:1px solid var(--border); padding:2px 6px; border-radius:4px; color:var(--text-subtle);">ESC</kbd>
          </div>
          <div class="cmd-results-list" id="cmdResultsList">
            <div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
              输入标题、行业或概念快速查找...
            </div>
          </div>
          <div class="cmd-modal-footer">
            <span>导航: <kbd>↑</kbd> <kbd>↓</kbd> 选择，<kbd>Enter</kbd> 查看</span>
            <span>按 <kbd>ESC</kbd> 退出</span>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      modal.addEventListener('click', (e) => {
        if (e.target === modal) this.close();
      });

      const input = modal.querySelector('#cmdSearchInput');
      input.addEventListener('input', () => this.handleQuery(input.value));
      input.addEventListener('keydown', (e) => this.handleKeydown(e));
    },

    bindEvents() {
      // Global shortcut: Cmd+K / Ctrl+K / '/'
      document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          this.toggle();
        } else if (e.key === 'Escape' && this.isOpen) {
          this.close();
        } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
          e.preventDefault();
          this.open();
        }
      });

      // Bind buttons with .cmd-search-trigger
      document.querySelectorAll('.cmd-search-trigger').forEach(btn => {
        btn.addEventListener('click', () => this.open());
      });
    },

    open() {
      const modal = document.getElementById('cmdSearchModal');
      if (!modal) return;
      modal.classList.add('active');
      this.isOpen = true;
      const input = modal.querySelector('#cmdSearchInput');
      input.value = '';
      this.renderInitial();
      setTimeout(() => input.focus(), 50);
    },

    close() {
      const modal = document.getElementById('cmdSearchModal');
      if (!modal) return;
      modal.classList.remove('active');
      this.isOpen = false;
    },

    toggle() {
      this.isOpen ? this.close() : this.open();
    },

    renderInitial() {
      const list = document.getElementById('cmdResultsList');
      if (!this.data || this.data.length === 0) {
        list.innerHTML = `<div style="padding:1.5rem; text-align:center; color:var(--text-muted); font-size:0.85rem;">加载研报索引中...</div>`;
        return;
      }
      this.renderItems(this.data.slice(0, 6), '最新收录研报');
    },

    handleQuery(query) {
      query = query.trim();
      const list = document.getElementById('cmdResultsList');
      if (!query) {
        this.renderInitial();
        return;
      }

      let results = [];
      if (this.fuse) {
        results = this.fuse.search(query).map(r => r.item);
      } else {
        const q = query.toLowerCase();
        results = this.data.filter(item => 
          item.title.toLowerCase().includes(q) || 
          item.desc.toLowerCase().includes(q) ||
          item.category.toLowerCase().includes(q)
        );
      }

      if (results.length === 0) {
        list.innerHTML = `
          <div style="padding:2.5rem; text-align:center; color:var(--text-muted);">
            <p style="font-size:1.1rem; margin-bottom:0.5rem;">未检索到相关研报</p>
            <p style="font-size:0.82rem;">尝试使用其它关键词，或在首页查看分类索引</p>
          </div>
        `;
        return;
      }

      this.renderItems(results.slice(0, 10), `检索结果 (${results.length})`);
    },

    renderItems(items, headerText) {
      const list = document.getElementById('cmdResultsList');
      const rootPath = document.body.getAttribute('data-root') || '';
      this.selectedIndex = -1;

      let html = `<div style="padding: 0.35rem 0.85rem; font-size: 0.72rem; font-weight: 700; color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.05em;">${headerText}</div>`;

      items.forEach((item, idx) => {
        const url = `${rootPath}reports/${encodeURIComponent(item.file || (item.slug + '.html'))}`;
        html += `
          <a href="${url}" class="cmd-result-item" data-idx="${idx}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
              <span class="cmd-result-title">${item.title}</span>
              <span style="font-size:0.75rem; background:var(--bg-subtle); border:1px solid var(--border); padding:2px 8px; border-radius:12px; color:var(--text-muted);">${item.category}</span>
            </div>
            <div class="cmd-result-desc">${item.desc}</div>
          </a>
        `;
      });

      list.innerHTML = html;
    },

    handleKeydown(e) {
      const items = document.querySelectorAll('.cmd-result-item');
      if (!items.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex + 1) % items.length;
        this.updateSelection(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex - 1 + items.length) % items.length;
        this.updateSelection(items);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
          items[this.selectedIndex].click();
        } else if (items[0]) {
          items[0].click();
        }
      }
    },

    updateSelection(items) {
      items.forEach((item, idx) => {
        if (idx === this.selectedIndex) {
          item.classList.add('selected');
          item.scrollIntoView({ block: 'nearest' });
        } else {
          item.classList.remove('selected');
        }
      });
    }
  };

  // 4. Reading Progress Bar & Floating Utility Controls (For Report Pages)
  const ReportTools = {
    init() {
      this.initProgressBar();
      this.initScrollSpy();
      this.initMermaidControls();
      this.initAsciiEnhancer();
      this.bindActions();
    },

    initProgressBar() {
      let pb = document.getElementById('readingProgress');
      if (!pb) {
        pb = document.createElement('div');
        pb.id = 'readingProgress';
        pb.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--accent-cyan));width:0%;z-index:9999;transition:width 0.1s ease;';
        document.body.appendChild(pb);
      }

      window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        pb.style.width = Math.min(100, Math.max(0, progress)) + '%';
      }, { passive: true });
    },

    initScrollSpy() {
      const headings = document.querySelectorAll('article h2, article h3, .report-body h2, .report-body h3');
      const tocLinks = document.querySelectorAll('.toc a, aside nav a');
      if (!headings.length || !tocLinks.length) return;

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
      }, { rootMargin: '0px 0px -70% 0px' });

      headings.forEach(h => observer.observe(h));
    },

    initMermaidControls() {
      if (!window.mermaid) return;

      document.querySelectorAll('pre code.language-mermaid, pre code.mermaid').forEach((block, idx) => {
        const pre = block.parentElement;
        const codeText = block.textContent;
        const wrapper = document.createElement('div');
        wrapper.className = 'mermaid-interactive-card';
        wrapper.innerHTML = `
          <div class="diag-header">
            <div class="diag-title">
              <span class="diag-badge">Mermaid</span>
              <span>结构与时序架构图 #${idx + 1}</span>
            </div>
            <div class="diag-controls">
              <button class="diag-btn" title="缩小" onclick="window.zoomMermaid(this, 0.85)">🔍-</button>
              <button class="diag-btn" title="重置" onclick="window.resetMermaid(this)">↺ 100%</button>
              <button class="diag-btn" title="放大" onclick="window.zoomMermaid(this, 1.25)">🔍+</button>
              <button class="diag-btn primary" title="全屏高清" onclick="window.fullscreenMermaid(this)">⛶ 全屏</button>
            </div>
          </div>
          <div class="diag-viewport">
            <div class="mermaid" data-scale="1.2" style="transform: scale(1.2); transform-origin: top center;">${codeText}</div>
          </div>
        `;
        pre.parentNode.replaceChild(wrapper, pre);
      });

      mermaid.initialize({
        startOnLoad: false,
        theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral',
        fontFamily: 'Plus Jakarta Sans, Noto Sans SC, sans-serif'
      });
      mermaid.run();
    },

    initAsciiEnhancer() {
      const asciiRegex = /[┌┬┐├┼┤└┴┘│─━┏┳┓┣╋┫┗┻┛┃═║╔╦╗╠╬╣╚╩╝▶►◄▼▲┼╭╮╯╰]/;
      let count = 0;
      document.querySelectorAll('.report-body pre, article pre').forEach((pre) => {
        if (pre.closest('.mermaid-interactive-card')) return;
        const text = pre.textContent;
        if (asciiRegex.test(text) || (text.includes('+--') && text.includes('|'))) {
          count++;
          pre.classList.add('ascii-chart');
          const wrapper = document.createElement('div');
          wrapper.className = 'ascii-interactive-card';
          wrapper.innerHTML = `
            <div class="ascii-header">
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:13px; color:#38bdf8;">📐</span>
                <span style="font-size:12.5px; font-weight:700; color:#cbd5e1;">系统架构与拓扑全景 #${count} (ASCII)</span>
              </div>
              <button class="ascii-copy-btn" onclick="window.copyAscii(this)">📋 复制拓扑结构</button>
            </div>
          `;
          pre.parentNode.insertBefore(wrapper, pre);
          wrapper.appendChild(pre);
        }
      });
    },

    bindActions() {
      window.zoomMermaid = function (btn, factor) {
        const vp = btn.closest('.mermaid-interactive-card').querySelector('.mermaid');
        const current = parseFloat(vp.getAttribute('data-scale') || '1.2');
        const next = Math.min(Math.max(current * factor, 0.6), 3.5);
        vp.setAttribute('data-scale', next.toFixed(2));
        vp.style.transform = `scale(${next.toFixed(2)})`;
      };

      window.resetMermaid = function (btn) {
        const vp = btn.closest('.mermaid-interactive-card').querySelector('.mermaid');
        vp.setAttribute('data-scale', '1.2');
        vp.style.transform = 'scale(1.2)';
      };

      window.fullscreenMermaid = function (btn) {
        const svg = btn.closest('.mermaid-interactive-card').querySelector('.mermaid svg');
        if (!svg) return;
        let modal = document.getElementById('diagFullscreenModal');
        if (!modal) {
          modal = document.createElement('div');
          modal.id = 'diagFullscreenModal';
          modal.className = 'diag-fullscreen-modal';
          modal.innerHTML = `
            <div class="diag-fullscreen-content">
              <button class="diag-fullscreen-close" onclick="this.closest('.diag-fullscreen-modal').classList.remove('active')">✕ 退出全屏</button>
              <div class="diag-fullscreen-body" id="diagFullscreenBody"></div>
            </div>
          `;
          document.body.appendChild(modal);
          modal.addEventListener('click', e => {
            if (e.target === modal) modal.classList.remove('active');
          });
        }
        const body = modal.querySelector('#diagFullscreenBody');
        body.innerHTML = svg.outerHTML;
        const targetSvg = body.querySelector('svg');
        if (targetSvg) {
          targetSvg.style.width = '100%';
          targetSvg.style.minWidth = '900px';
          targetSvg.style.height = 'auto';
        }
        modal.classList.add('active');
      };

      window.copyAscii = function (btn) {
        const pre = btn.closest('.ascii-interactive-card').querySelector('pre');
        navigator.clipboard.writeText(pre.innerText).then(() => {
          showToast('拓扑结构已成功复制到剪贴板！');
        });
      };
    }
  };

  // Initialize on DOM Ready
  document.addEventListener('DOMContentLoaded', () => {
    Theme.init();
    Search.init();

    // Bind theme toggles
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => Theme.toggle());
    });

    // Check if this is a report details page
    if (document.querySelector('article, .report-body')) {
      ReportTools.init();
    }
  });

  window.HV_Theme = Theme;
  window.HV_Search = Search;
})();
