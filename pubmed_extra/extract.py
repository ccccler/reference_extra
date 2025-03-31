import pandas as pd
import aiohttp
import asyncio
from lxml import html
import time
import ssl
from concurrent.futures import ThreadPoolExecutor

async def extract_pubmed_info_async(url, session, semaphore):
    # 使用信号量控制并发
    async with semaphore:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {
                        'background': '',
                        'methods': '',
                        'results': '',
                        'conclusion': '',
                        'keywords': '',
                        'mesh_terms': ''
                    }
                    
                content = await response.text()
                tree = html.fromstring(content)
                
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

async def process_batch_async(urls, max_concurrent=5):
    print(f"Processing batch with {len(urls)} URLs")
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # 创建SSL上下文并禁用验证
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 在创建session时添加SSL配置
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for url in urls:
            if pd.notna(url):
                await asyncio.sleep(0.1)
                tasks.append(extract_pubmed_info_async(url, session, semaphore))
        
        results = await asyncio.gather(*tasks)
        print(f"Batch of {len(urls)} URLs completed")
        return results

def process_excel_async(excel_path, url_column, max_concurrent=5, batch_size=50):
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
    
    # 计算批次数
    total_urls = len(urls)
    num_batches = (total_urls + batch_size - 1) // batch_size
    
    # 按批次处理
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_urls)
        
        print(f"\nProcessing batch {batch_num + 1}/{num_batches}")
        print(f"URLs {start_idx + 1} to {end_idx}")
        
        # 获取当前批次的URLs
        batch_urls = urls[start_idx:end_idx]
        
        # 处理当前批次
        results = asyncio.run(process_batch_async(batch_urls, max_concurrent))
        
        # 更新DataFrame
        for i, result in enumerate(results):
            current_idx = start_idx + i
            if pd.notna(df.iloc[current_idx][url_column]):
                df.at[current_idx, 'Background'] = result['background']
                df.at[current_idx, 'Methods'] = result['methods']
                df.at[current_idx, 'Results/Findings'] = result['results']
                df.at[current_idx, 'Conclusion/Interpretation'] = result['conclusion']
                df.at[current_idx, 'Keywords'] = result['keywords']
                df.at[current_idx, 'MeSH_Terms'] = result['mesh_terms']
                print(f"Processed URL {current_idx + 1}/{total_urls}")
        
        # 每批次完成后保存一次结果
        output_path = 'pubmed_results.xlsx'
        df.to_excel(output_path, index=False)
        print(f"Intermediate results saved to {output_path}")
        
        # 批次间延迟
        if batch_num < num_batches - 1:
            print("Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    print("\nAll batches completed!")
    print(f"Final results saved to {output_path}")

if __name__ == "__main__":
    excel_path = "./output_ref/NCCN-BreastCancer_2024.V5_EN_NCCN_pubmed.xlsx"
    url_column = "url"
    max_concurrent = 5  # 每批次中的最大并发数
    batch_size = 50    # 每批次处理的URL数量
    process_excel_async(excel_path, url_column, max_concurrent, batch_size)
