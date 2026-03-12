import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

def get_atis():
    url = "https://atis.cad.gov.hk/ATIS/ATISweb/atis.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取网页文本内容
        content = soup.get_text(separator='\n').strip()
        return content
    except Exception as e:
        return f"Error fetching ATIS: {str(e)}"

def run():
    # 1. 设置香港时区
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    now = datetime.now(hk_tz)
    
    # 2. 生成文件名：atis_20231027.txt
    date_str = now.strftime("%Y%m%d")
    filename = f"atis_{date_str}.txt"
    
    # 3. 获取 ATIS 内容
    content = get_atis()
    
    # 4. 准备写入的内容格式（带上具体的小时分钟）
    timestamp = now.strftime("%H:%M:%S")
    entry = f"\n{'='*15} HK Time: {timestamp} {'='*15}\n{content}\n"
    
    # 5. 写入文件 ("a" 模式：如果文件不存在会创建，存在则追加)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Successfully recorded to {filename}")

if __name__ == "__main__":
    run()
