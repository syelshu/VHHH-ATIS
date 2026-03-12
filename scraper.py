import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

# 将需要忽略的、固定的备注文本定义为一个常量，
# 保持多行格式，以便我们能将其解析为行列表。
REMARKS_BLOCK_TEXT = '''Remarks:
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
        
        # 1. 抓取网页原始文本，使用 \n 作为分隔符以保留初始行结构
        content_raw = soup.get_text(separator='\n')
        
        # 2. 将原始网页文本解析为干净的行列表，去掉每行首尾空格，去掉空行
        # 这里绝对不能线性化，必须保留行列表结构
        scraped_lines = [line.strip() for line in content_raw.splitlines() if line.strip()]
        
        # 3. 解析目标备注为干净的行列表
        ignore_lines = [line.strip() for line in REMARKS_BLOCK_TEXT.splitlines() if line.strip()]
        
        n_ignore = len(ignore_lines)
        match_index = -1
        
        # 4. **核心修改：精准匹配行序列**
        # 遍历网页行列表，寻找连续匹配 ignore_lines 的序列
        for i in range(len(scraped_lines) - n_ignore + 1):
            if scraped_lines[i : i + n_ignore] == ignore_lines:
                match_index = i
                break
        
        # 5. **核心修改：精准“切片”删除**
        if match_index != -1:
            # 使用列表切片赋值，将匹配的序列从原列表中整体“抠掉”
            # 这是一个高效且安全的删除方式
            del scraped_lines[match_index : match_index + n_ignore]
        
        # 6. 将处理后的行列表（此时已去掉备注，且其余排版未变）
        # 使用换行符原样组合起来
        content = '\n'.join(scraped_lines)
        
        if not content:
            return "(未能抓取到有效 ATIS 文本，请检查网页结构)"
            
        return content
    except Exception as e:
        return f"Error fetching ATIS: {str(e)}"

def run():
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    now = datetime.now(hk_tz)
    
    # 保留文件夹和文件名逻辑
    output_dir = 'atis'
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = now.strftime("%Y%m%d")
    base_filename = f"vhhh_{date_str}.txt"
    full_filename = os.path.join(output_dir, base_filename)
    
    # 获取并处理动态 ATIS 内容（**过滤 Remarks 和保留排版在这里实现**）
    content = get_atis()
    
    # 保持简洁的时间戳和紧凑的写入格式
    timestamp = now.strftime("%H:%M")
    entry = f"[HKT: {timestamp}]\n{content}\n"
    
    with open(full_filename, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Successfully recorded compact, formatted log to {full_filename}")

if __name__ == "__main__":
    run()
