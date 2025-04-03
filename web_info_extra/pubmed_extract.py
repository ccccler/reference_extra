import pandas as pd
import requests
from lxml import html
import time

def extract_pubmed_info(url):
    try:
        # 添加延迟以避免过快请求
        # time.sleep(0.2)
        
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'pm-csrf=jlQtCXnCSYbhwhf3RC2uNM1BBomsajuE'
        }
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # 解析页面内容
        tree = html.fromstring(response.content)
        
        # 提取各个部分
        background = tree.xpath('//*[@id="eng-abstract"]/p[1]/text()')
        background = ' '.join(background).strip()
        
        methods = tree.xpath('//*[@id="eng-abstract"]/p[2]/text()')
        methods = ' '.join(methods).strip()
        
        results = tree.xpath('//*[@id="eng-abstract"]/p[3]/text()')
        results = ' '.join(results).strip()
        
        conclusion = tree.xpath('//*[@id="eng-abstract"]/p[4]/text()')
        if not conclusion:
            conclusion = tree.xpath('//*[@id="eng-abstract"]/p[4]/text()[1]')
        conclusion = ' '.join(conclusion).strip()
        
        keywords = tree.xpath('//*[@id="abstract"]/p/text()')
        keywords = ' '.join(keywords).strip()
        
        mesh_terms = tree.xpath('//*[@id="mesh-terms"]/ul//button[contains(@class, "keyword-actions-trigger")]/text()')
        mesh_terms = [term.strip() for term in mesh_terms if term.strip()]
        mesh_terms = '; '.join(mesh_terms)
        
        return {
            'background': background,
            'methods': methods,
            'results': results,
            'conclusion': conclusion,
            'keywords': keywords,
            'mesh_terms': mesh_terms
        }
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return {
            'background': '',
            'methods': '',
            'results': '',
            'conclusion': '',
            'keywords': '',
            'mesh_terms': ''
        }

def process_excel(excel_path, url_column, batch_size=30):
    # 读取Excel文件
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"Found {len(df)} rows in Excel file")
    
    # 创建新列
    df['Background'] = ''
    df['Methods'] = ''
    df['Results/Findings'] = ''
    df['Conclusion/Interpretation'] = ''
    df['Keywords'] = ''
    df['MeSH_Terms'] = ''
    
    # 获取所有URL
    urls = df[url_column].tolist()
    total_urls = len(urls)
    
    # 计算批次数
    num_batches = (total_urls + batch_size - 1) // batch_size
    
    # 按批次处理
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_urls)
        
        print(f"\nProcessing batch {batch_num + 1}/{num_batches}")
        print(f"URLs {start_idx + 1} to {end_idx}")
        
        # 处理当前批次的URL
        for i in range(start_idx, end_idx):
            url = urls[i]
            if pd.notna(url):
                print(f"Processing URL {i + 1}/{total_urls}: {url}")
                result = extract_pubmed_info(url)
                
                # 更新DataFrame
                df.at[i, 'Background'] = result['background']
                df.at[i, 'Methods'] = result['methods']
                df.at[i, 'Results/Findings'] = result['results']
                df.at[i, 'Conclusion/Interpretation'] = result['conclusion']
                df.at[i, 'Keywords'] = result['keywords']
                df.at[i, 'MeSH_Terms'] = result['mesh_terms']
        
        # 每批次完成后保存一次结果
        output_path = 'pubmedinfo/CSCO_乳腺癌诊疗指南2023_pubmed.xlsx'
        df.to_excel(output_path, index=False)
        print(f"Intermediate results saved to {output_path}")
        
        # 批次间延迟
        if batch_num < num_batches - 1:
            print("Waiting 5 seconds before next batch...")
            time.sleep(0.1)
    
    print("\nAll batches completed!")
    print(f"Final results saved to {output_path}")

if __name__ == "__main__":
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    excel_path = "chinese_zels/CSCO_乳腺癌诊疗指南2023_elasticsearch.xlsx"
    url_column = "pubmed_url"
    batch_size = 30    # 每批次处理的URL数量
    process_excel(excel_path, url_column, batch_size)
