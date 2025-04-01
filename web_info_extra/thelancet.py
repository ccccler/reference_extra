import pandas as pd
import requests
from lxml import html
import time

def extract_info_from_url(url):
    try:
        # 根据你的浏览器实际请求头修改
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Sec-Ch-Ua': '"Chromium";v="134", "Not-A-Brand";v="24", "Google Chrome";v="134"',
            'Sec-Ch-Ua-Arch': '"x86"',
            'Sec-Ch-Ua-Bitness': '"64"',
            'Sec-Ch-Ua-Full-Version': '"134.0.6998.166"',
            'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="134.0.6998.166", "Not-A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.166"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Model': '""',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Ch-Ua-Platform-Version': '"12.3.0"',
            'Referer': 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(11)60070-6/abstract',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 添加session来维持连接
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析HTML
        tree = html.fromstring(response.content)
        
        # 提取三个部分的内容
        background = tree.xpath('//*[@id="spara200"]/text()')
        methods = tree.xpath('//*[@id="spara210"]/text()')
        findings = tree.xpath('//*[@id="spara220"]/text()')
        
        # 处理提取的内容
        background = ' '.join(background).strip() if background else ''
        methods = ' '.join(methods).strip() if methods else ''
        findings = ' '.join(findings).strip() if findings else ''
        
        return {
            'background': background,
            'methods': methods,
            'findings': findings
        }
        
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return {
            'background': '',
            'methods': '',
            'findings': ''
        }

def main():
    try:
        # 读取Excel文件
        # 请将'your_file.xlsx'替换为你的Excel文件名
        # 'urls'替换为包含URL的列名
        df = pd.read_excel('inside_reference/NCCN_2024v5_middle_output_url.xlsx')
        
        # 创建存储结果的列表
        results = []
        
        # 处理每个URL
        for index, row in df.iterrows():
            url = row['url']  # 替换'urls'为你的URL列名
            print(f"Processing URL {index + 1}: {url}")
            
            # 提取信息
            info = extract_info_from_url(url)
            info['url'] = url
            results.append(info)
            
            # 添加延时以避免请求过于频繁
            time.sleep(2)
        
        # 创建结果DataFrame
        results_df = pd.DataFrame(results)
        
        # 保存结果到新的Excel文件
        results_df.to_excel('extracted_results.xlsx', index=False)
        print("Extraction completed. Results saved to 'extracted_results.xlsx'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
