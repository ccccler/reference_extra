import aiohttp
import asyncio
import json
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BackgroundProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 100):
        self.api_key = api_key
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def call_api_sse(self, abstract: str, idx: int) -> Dict:
        """使用SSE方式调用API"""
        url = 'http://192.168.1.90:5000/v1/completion-messages'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 修改提示词模板
        prompt = f"""
        # 你是一名医学专家，你的任务是从文献摘要中提取出这篇文献中医学相关的关键词，用于在之后的检索能够找到它。
        关键词需要体现这篇文献的核心，并且具有区分度能够与其它文献进行区分，如果有某些具备区分度的医学名词的简写，请额外分析并选择是否可以成为关键词。
        关键词使用英文，并且只输出你提炼的关键词。要求以列表格式输出。注意，只允许返回列表格式，不要输出其他内容。 如果输入内容为空，则返回null。 
        
        # 请严格按照以下列表格式输出分析结果：
        "keywords": ["关键词1", "关键词2", "关键词3"]
        

        # 研究摘要：{abstract}
        """

        data = {
            "inputs": {"query": prompt},
            "response_mode": "blocking",
            "user": "background_processor"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, json=data, timeout=None) as response:
                    if response.status != 200:
                        raise Exception(f"API返回错误状态码: {response.status}")
                    
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                        model_response = response_data.get('answer', '')
                        print(f"✓ 完成第 {idx+1} 条背景信息处理")

                        return {
                            "id": idx,
                            "original_abstract": abstract,
                            "keywords": model_response.strip()  # 只做简单的空格处理
                        }
                    except json.JSONDecodeError as e:
                        raise Exception(f"JSON解析错误: {e}")

        except Exception as e:
            print(f"✗ 第 {idx+1} 条背景信息处理失败: {str(e)}")
            return {
                "id": idx,
                "original_abstract": abstract,
                "keywords": f"ERROR: {str(e)}"
            }

    async def process_abstract(self, abstract: str, idx: int) -> Dict:
        """处理单条背景信息"""
        async with self.semaphore:
            await asyncio.sleep(0.1)
            return await self.call_api_sse(abstract, idx)

    async def process_all_abstracts(self, abstracts: List[str]):
        """处理所有背景信息"""
        tasks = [self.process_abstract(abstract, idx) for idx, abstract in enumerate(abstracts)]
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理可能的异常
        self.results = [
            result if not isinstance(result, Exception)
            else {"id": idx, "original_abstract": abstracts[idx], "keywords": f"ERROR: {str(result)}"}
            for idx, result in enumerate(self.results)
        ]
        
        print(f"\n全部处理完成！共处理 {len(abstracts)} 条摘要信息")

    def save_to_excel(self, output_file: str, titles: List[str], pubmed_ids: List[str], pubmed_urls: List[str], mesh_terms: List[str]):
        """将结果保存到Excel文件"""
        df = pd.DataFrame(self.results)
        df['es_title'] = titles  # 添加标题列
        df['pubmed_id'] = pubmed_ids  # 添加 PubMed ID 列
        df['pubmed_url'] = pubmed_urls  # 添加 PubMed URL 列
        df['mesh_terms'] = mesh_terms  # 添加 MeSH Terms 列
        df = df[['id', 'es_title', 'pubmed_id', 'pubmed_url', 'mesh_terms', 'original_abstract', 'keywords']]  # 调整列顺序
        df.to_excel(output_file, index=False)

async def main():
    # 读取JSON文件并提取Background/Purpose字段
    with open('abcom_output_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    abstracts = [item.get('abstract', '') for item in data]  # 修改字段名
    titles = [item.get('Title', '') for item in data]  # 添加标题字段
    pubmed_ids = [item.get('pubmed_id', '') for item in data]  # 添加标题字段
    pubmed_urls = [item.get('pubmed_url', '') for item in data]  # 添加标题字段
    mesh_terms = [item.get('MeSH_Terms', '') for item in data]  # 添加标题字段

    # 初始化处理器
    processor = BackgroundProcessor(api_key="app-0vDNiDJUUz7usGZqLn9L1moo", max_concurrent=100)
    
    # 处理所有背景信息
    await processor.process_all_abstracts(abstracts)
    
    # 生成输出文件名
    output_file = f"abstract_terms_analysis.xlsx"
    
    # 保存结果
    processor.save_to_excel(output_file, titles, pubmed_ids, pubmed_urls, mesh_terms)  # 传入标题列表
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
