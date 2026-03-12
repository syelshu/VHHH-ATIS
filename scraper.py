import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

# 将那段需要忽略的、固定的排版文本定义为一个常量
# 使用多行字符串 ('''...''')，并将每一行的空白字符去掉，以确保匹配准确
REMARKS_TO_IGNORE = '''Remarks:
The
ATIS will be updated whenever there are significant changes in content. Owing
to technical differences such as averaging periods, reference locations and
updating mechanisms, the meteorological information shown on the ATIS might be
different from that available on the Aviation Weather Report Page.'''

def get_atis():
    url = "https://atis.cad.gov.hk/ATIS/ATISweb/atis.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 抓取网页所有原始文本，保留换行符
        content_raw = soup.get_text(separator='\n')
        
        # 2. **核心修改**: 精确匹配并替换掉那段固定的备注文本
        # 我们先清理 REMARKS_TO_IGNORE 本身的格式，将其行与行合并为一个干净的字符串用于匹配
        # 同时也将 content_raw 处理得更干净，以便匹配
        cleaned_ignore_text = ' '.join([line.strip() for line in REMARKS_TO_IGNORE.splitlines() if line.strip()])
        cleaned_content_raw = ' '.join([line.strip() for line in content_raw.splitlines() if line.strip()])
        
        # 使用 replace 方法将那段固定备注替换为空（即删除）
        if cleaned_ignore_text in cleaned_content_raw:
            content_cleaned = cleaned_content_raw.replace(cleaned_ignore_text, "").strip()
        else:
            # 如果万一没匹配到（比如网页排版微调），我们就保留原文本，防止意外删除了有用的 ATIS 内容
            content_cleaned = cleaned_content_raw
            
        # 3. 再将清理后的内容（目前是单行）重新按原本的 ATIS 格式整理
        # 这里需要更精细的处理，保留原本的 DEP 和 ARR 换行
        final_atis_lines = []
        words = content_cleaned.split()
        current_line_words = []
        
        # 简单的重新整理逻辑：遇到 DEP ATIS 或 ARR ATIS 就换行
        # 这不是完美的，但比之前的方法更稳健，因为它不会因为 ATIS 内部的 "Remarks:" 而截断。
        for word in words:
            if word in ["DEP", "ARR"]:
                if current_line_words:
                    final_atis_lines.append(' '.join(current_line_words))
                current_line_words = [word]
            else:
                current_line_words.append(word)
        
        if current_line_words:
            final_atis_lines.append(' '.join(current_line_words))
            
        content = '\n'.join(final_atis_lines)
        
        if not content:
            return "(未能抓取到有效 ATIS 文本，请检查网页结构)"
            
        return content
    except Exception as e:
        return f"Error fetching ATIS: {str(e)}"

def run():
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    now = datetime.now(hk_tz)
    
    output_dir = 'atis'
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = now.strftime("%Y%m%d")
    base_filename = f"vhhh_{date_str}.txt"
    full_filename = os.path.join(output_dir, base_filename)
    
    # 获取并清洗 ATIS 内容（**过滤 Remarks 在这里实现**）
    content = get_atis()
    
    timestamp = now.strftime("%H:%M")
    entry = f"[HKT: {timestamp}]\n{content}\n"
    
    with open(full_filename, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Successfully recorded compact log (filtered remarks) to {full_filename}")

if __name__ == "__main__":
    run()
