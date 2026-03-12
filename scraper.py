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
        # 显式指定编码，防止中文或特殊字符乱码
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 抓取网页所有原始文本
        content_raw = soup.get_text(separator='\n')
        
        # 2. 精炼内容（关键步骤！）
        # 将原始文本按行拆分，对每一行去除首尾空格。
        # 然后，只保留那些去掉空格后不为空的内容行。
        cleaned_lines = [line.strip() for line in content_raw.splitlines() if line.strip()]
        
        # 将精炼后的内容重新组合，每行之间只保留一个换行符
        content = '\n'.join(cleaned_lines)
        
        # 如果清洗后内容为空，返回提示
        if not content:
            return "(未能抓取到有效 ATIS 文本，请检查网页结构)"
            
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
    
    # 3. 获取并清洗 ATIS 内容
    content = get_atis()
    
    # 4. 准备紧凑的写入格式
    timestamp = now.strftime("%H:%M") # 只精确到分，更简洁
    
    # 格式调整为：[HKT 时间] 内容 (不再使用大量的换行符和等号)
    entry = f"[HKT: {timestamp}]\n{content}\n"
    
    # 5. 写入文件 ("a" 模式：如果文件不存在会创建，存在则追加)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Successfully recorded compact log to {filename}")

if __name__ == "__main__":
    run()
