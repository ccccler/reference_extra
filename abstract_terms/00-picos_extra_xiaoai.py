import aiohttp
import asyncio
import json
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BackgroundProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.api_key = "sk-kvH38CjwA1PTazUrgmF0WR8I1s8sjtHd6TveYTYAxddEfMQh"
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def call_api_sse(self, abstract: str, idx: int) -> Dict:
        """使用API调用"""
        url = 'https://xiaoai.plus/v1/chat/completions'  # 修改为新的API endpoint
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 修改消息格式以匹配新的API
        messages = [
            {
                "role": "system",
                "content": """
                # 你是一个医学论文的标签提取助手，能够协助提取每篇医学文献的关键词，方便特定领域Meta分析的撰写。，我会提供给你一份论文摘要，请你仔细阅读摘要，从中提取出相关关键词。
                关键词的提取分为两条路线，第一条路线是根据循证医学中的PICOS原则，从摘要中提取出该研究对应PICOS的研究关键词。
                第二条路线是提取研究内容，识别其对应的MeSHTerm关键词。
                关键词以英文反馈，要求以json格式输出。注意，只允许返回json格式，不要输出其他内容。
                
                # 请严格按照以下json格式输出分析结果：  
                {{
                    "PICOS": {{ 
                        "Participant/Patients": "", 
                        "Intervention/Exposure": "",  
                        "Comparison": "",
                        "Outcome": "",
                        "Study Design": ""
                    }},
                    "MeSHTerm": {{
                        "MeSHTerm1": "",
                        "MeSHTerm2": "",
                        "MeSHTerm3": "",
                        ......
                    }}
                }}
                """
            },
            {
                "role": "user",
                "content": f"# 研究摘要：{abstract}"
            }
        ]

        data = {
            "messages": messages,
            "stream": False,
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_p": 1
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, json=data, timeout=None) as response:
                    if response.status != 200:
                        raise Exception(f"API返回错误状态码: {response.status}")
                    
                    response_data = await response.json()
                    # 从新的API响应格式中提取内容
                    model_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✓ 完成第 {idx+1} 条背景信息处理")

                    return {
                        "id": idx,
                        "original_abstract": abstract,
                        "model_response": model_response.strip()
                    }

        except Exception as e:
            print(f"✗ 第 {idx+1} 条背景信息处理失败: {str(e)}")
            return {
                "id": idx,
                "original_abstract": abstract,
                "model_response": f"ERROR: {str(e)}"
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
            else {"id": idx, "original_abstract": abstracts[idx], "model_response": f"ERROR: {str(result)}"}
            for idx, result in enumerate(self.results)
        ]
        
        print(f"\n全部处理完成！共处理 {len(abstracts)} 条摘要信息")

    def save_to_excel(self, output_file: str, titles: List[str]):
        """将结果保存到Excel文件"""
        df = pd.DataFrame(self.results)
        df['es_title'] = titles  # 添加标题列
        df = df[['id', 'es_title', 'original_abstract', 'model_response']]  # 调整列顺序
        df.to_excel(output_file, index=False)

async def main():
    # 读取JSON文件并提取Background/Purpose字段
    with open('./reference_extra/output_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    abstracts = [item.get('abstract', '') for item in data]  # 修改字段名
    titles = [item.get('es_title', '') for item in data]  # 添加标题字段

    # 初始化处理器
    processor = BackgroundProcessor(api_key="sk-kvH38CjwA1PTazUrgmF0WR8I1s8sjtHd6TveYTYAxddEfMQh", max_concurrent=10)
    
    # 处理所有背景信息
    await processor.process_all_abstracts(abstracts)
    
    # 生成输出文件名
    output_file = f"abstract_terms_analysis.xlsx"
    
    # 保存结果
    processor.save_to_excel(output_file, titles)  # 传入标题列表
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
