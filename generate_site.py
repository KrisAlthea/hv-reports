import os, json, glob, re
from bs4 import BeautifulSoup

REPORTS_DIR = '/root/projects/hv-reports/reports'
OUTPUT_INDEX = '/root/projects/hv-reports/search-index.json'

CATEGORY_MAP = {
    '美联储': ('宏观与金融', '🏛️ 宏观货币'),
    '美股三大指数': ('宏观与金融', '📈 资本市场'),
    '中国四大酒店': ('商业与消费', '🏨 酒店文旅'),
    '华纳兄弟': ('商业与消费', '🎬 传媒娱乐'),
    '美国主要动画': ('商业与消费', '🎨 文化产业'),
    '天津': ('产业与制造', '🏙️ 区域经济'),
    '烟台东方威思顿': ('产业与制造', '⚡ 电力设备'),
    'fde': ('AI与科技', '🤖 AI工程化'),
    'welcome': ('方法论', '📖 核心范式')
}

reports = []
for p in sorted(glob.glob(f'{REPORTS_DIR}/*.html')):
    fname = os.path.basename(p)
    with open(p, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    title_el = soup.find('h1') or soup.find('title')
    raw_title = title_el.get_text().strip() if title_el else fname.replace('.html', '')
    title = re.sub(r'\s*\|\s*HV Analysis.*$', '', raw_title).strip()
    
    cat = '深度研报'
    tag = '📊 产业研究'
    for k, v in CATEGORY_MAP.items():
        if k.lower() in fname.lower() or k.lower() in title.lower():
            cat, tag = v
            break
            
    p_tags = soup.find_all('p')
    desc = ''
    for pt in p_tags:
        text = pt.get_text().strip()
        if len(text) > 40 and not text.startswith('作者') and not text.startswith('时间'):
            desc = text[:220]
            break
    if not desc and p_tags:
        desc = p_tags[0].get_text().strip()[:200]
        
    date_match = re.search(r'202[4-6][-\.年]\d{1,2}', soup.get_text())
    date_str = date_match.group(0).replace('年', '-').replace('.', '-') if date_match else '2026-08'
    if len(date_str) == 6 and date_str[4] == '-':
        date_str = f"{date_str[:5]}0{date_str[5]}"
        
    full_text = ' '.join(soup.get_text().split())
    char_count = len(full_text)
    read_time = max(3, round(char_count / 500))
    
    reports.append({
        'slug': fname.replace('.html', ''),
        'filename': fname,
        'title': title,
        'category': cat,
        'tag': tag,
        'desc': desc,
        'date': date_str,
        'char_count': char_count,
        'read_time': f"{read_time} 分钟",
        'summary': desc[:160] + '...'
    })

reports.sort(key=lambda x: (x['category'] != '方法论', x['date']), reverse=True)

with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
    json.dump(reports, f, ensure_ascii=False, indent=2)

print(f"Generated search index with {len(reports)} reports.")
