import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

# 定义一个辅助函数，用于过滤页脚备注
def filter_remarks(lines):
    # 这是我们用来判断 Remarks 或页脚开始的关键字列表
    # 你可以根据实际观察到的网页内容在这个列表中添加更多关键字
    footer_keywords = [
        "Copyright",
        "Civil Aviation Department",
        "Important Notice",
        "Privacy Policy"
    ]
    
    filtered_content = []
    for line in lines:
        # 如果当前行包含任何页脚关键字，我们就停止处理并返回之前的内容
        if any(keyword in line for keyword in footer_keywords):
            break
        # 否则，将这一行添加到过滤后的内容中
        filtered_content.append(line)
        
    return filtered_content

def get_atis():
    url = "https://atis.cad.gov.hk/ATIS/ATISweb/atis.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 抓取网页所有原始文本
        content_raw = soup.get_text(separator='\n')
        
        # 2. 精炼内容：去掉空白行
        cleaned_lines = [line.strip() for line in content_raw.splitlines() if line.strip()]
        
        # 3. 过滤 Remarks：使用辅助函数过滤页脚
        # 这将过滤掉 cleaned_lines 列表中页脚关键字之后的所有内容
        atis_lines = filter_remarks(cleaned_lines)
        
        # 4. 将过滤后的内容重新组合
        content = '\n'.join(atis_lines)
        
        # 如果过滤后内容为空，返回提示
        if not content:
            return "(未能抓取到有效 ATIS 文本，请检查网页结构)"
            
        return content
    except Exception as e:
        return f"Error fetching ATIS: {str(e)}"

def run():
    # 1. 设置香港时区
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    now = datetime.now(hk_tz)
    
    # 2. 修改：把所有文件放在 'atis' 文件夹下
    output_dir = 'atis'
    # 创建文件夹（如果它不存在的话），exist_ok=True 确保它不会因为文件夹已存在而报错
    os.makedirs(output_dir, exist_ok=True)
    
    # 3. 修改：生成新的文件名格式 vhhh_20231027.txt
    date_str = now.strftime("%Y%m%d")
    base_filename = f"vhhh_{date_str}.txt"
    
    # 组合完整的路径：'atis/vhhh_20231027.txt'
    full_filename = os.path.join(output_dir, base_filename)
    
    # 4. 获取并清洗 ATIS 内容
    content = get_atis()
    
    # 5. 准备紧凑的写入格式
    timestamp = now.strftime("%H:%M")
    entry = f"[HKT: {timestamp}]\n{content}\n"
    
    # 6. 写入文件 ("a" 模式：如果文件不存在会创建，存在则追加)
    with open(full_filename, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Successfully recorded compact log to {full_filename}")

if __name__ == "__main__":
    run()
