import json, os, glob, re
from bs4 import BeautifulSoup

REPORTS_DIR = '/root/projects/hv-reports/reports'
OUTPUT_INDEX = '/root/projects/hv-reports/index.html'
SEARCH_INDEX = '/root/projects/hv-reports/search-index.json'

CATEGORY_MAP = {
    '美联储加息与降息_横纵分析报告.html': {'cat': '宏观与金融', 'tag': '宏观与金融', 'icon': '📈', 'date': '2026-08', 'min': '14'},
    '美股三大指数与衍生生态_横纵分析报告.html': {'cat': '宏观与金融', 'tag': '宏观与金融', 'icon': '📊', 'date': '2026-08', 'min': '18'},
    'fde-analysis.html': {'cat': 'AI与科技', 'tag': 'AI与科技', 'icon': '🤖', 'date': '2026-09-08', 'min': '16'},
    'welcome.html': {'cat': '方法论', 'tag': '方法论', 'icon': '🧭', 'date': '2026-09-08', 'min': '6'},
    '中国四大酒店集团国内布局与发展策略横纵分析报告.html': {'cat': '商业与消费', 'tag': '商业与消费', 'icon': '🏨', 'date': '2026-08', 'min': '15'},
    '华纳兄弟_横纵分析报告.html': {'cat': '商业与消费', 'tag': '商业与消费', 'icon': '🎬', 'date': '2026-08', 'min': '16'},
    '美国主要动画片厂_横纵分析报告.html': {'cat': '商业与消费', 'tag': '商业与消费', 'icon': '🎨', 'date': '2026-08', 'min': '12'},
    '天津_横纵分析报告.html': {'cat': '产业与制造', 'tag': '产业与制造', 'icon': '🏙️', 'date': '2026-08', 'min': '20'},
    '烟台东方威思顿电气有限公司_横纵分析报告.html': {'cat': '产业与制造', 'tag': '产业与制造', 'icon': '⚡', 'date': '2026-08', 'min': '12'}
}

files = sorted(glob.glob(os.path.join(REPORTS_DIR, '*.html')))
reports_data = []

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    title_el = soup.find('h1') or soup.find('title')
    title = title_el.get_text().strip() if title_el else fname
    title = re.sub(r'[\r\n\t]+', ' ', title).strip()
    
    meta_cfg = CATEGORY_MAP.get(fname, {
        'cat': '深度研报', 'tag': '深度研报', 'icon': '📄', 'date': '2026-09', 'min': '10'
    })
    
    # Text snippet for search
    body_el = soup.find('article') or soup.find(class_='report-body') or soup.find('main') or soup.body
    body_text = body_el.get_text() if body_el else ''
    body_clean = ' '.join(body_text.split())
    
    # Extract h2 sections
    sections = []
    for h in soup.find_all(['h2', 'h3']):
        htxt = h.get_text().strip()
        hid = h.get('id', '')
        if htxt and len(htxt) < 35:
            sections.append({'id': hid, 'title': htxt})
            
    reports_data.append({
        'file': fname,
        'url': f'reports/{fname}',
        'title': title,
        'cat': meta_cfg['cat'],
        'tag': meta_cfg['tag'],
        'icon': meta_cfg['icon'],
        'date': meta_cfg['date'],
        'min': meta_cfg['min'],
        'words': len(body_clean),
        'summary': body_clean[:320] + '...',
        'sections': sections[:8]
    })

# Save search index
with open(SEARCH_INDEX, 'w', encoding='utf-8') as sf:
    json.dump(reports_data, sf, ensure_ascii=False, indent=2)

print(f"Generated search index with {len(reports_data)} reports.")
