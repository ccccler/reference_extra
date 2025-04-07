import aiohttp
import asyncio
import json
from typing import Dict, List
import pandas as pd

class ResultsProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.api_key = api_key
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def call_api_sse(self, Results: str, idx: int) -> Dict:
        """使用SSE方式调用API"""
        url = 'http://192.168.1.90:5000/v1/completion-messages'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 修改提示词模板
        prompt = f"""
        # 你是一个医学论文提取助手，请从医学论文摘要的“结果（Results）”部分提取出研究结果相关的关键词。
        结果部分通常包括研究的主要发现、数据呈现、统计分析结果（如p值、效应大小等）、实验组与对照组的对比等内容。你可以参考这些方面来提取关键词，并且以re_term1,re_term2,re_term3...的形式返回。
        关键词以英文反馈，要求以json格式输出，注意，只允许返回json格式，不要输出其他内容。
        请按照以下json格式输出分析结果：
        {{
            "re_term1": "", 
            "re_term2": "", 
            "re_term3": "",
            ......
        }}

        # 研究结果（Results）部分：{Results}


        """

        data = {
            "inputs": {"query": prompt},
            "response_mode": "blocking",
            "user": "Results_processor"
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
                            "original_Results": Results,
                            "model_response": model_response.strip()
                        }
                    except json.JSONDecodeError as e:
                        raise Exception(f"JSON解析错误: {e}")

        except Exception as e:
            print(f"✗ 第 {idx+1} 条背景信息处理失败: {str(e)}")
            return {
                "id": idx,
                "original_Results": Results,
                "model_response": f"ERROR: {str(e)}"
            }

    async def process_Results(self, Results: str, idx: int) -> Dict:
        """处理单条背景信息"""
        async with self.semaphore:
            await asyncio.sleep(0.1)
            return await self.call_api_sse(Results, idx)

    async def process_all_Results(self, Results: List[str]):
        """处理所有背景信息"""
        tasks = [self.process_Results(bg, idx) for idx, bg in enumerate(Results)]
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理可能的异常
        self.results = [
            result if not isinstance(result, Exception)
            else {"id": idx, "original_Results": Results[idx], "model_response": f"ERROR: {str(result)}"}
            for idx, result in enumerate(self.results)
        ]
        
        print(f"\n全部处理完成！共处理 {len(Results)} 条背景信息")

    def save_to_excel(self, output_file: str):
        """将结果保存到Excel文件"""
        df = pd.DataFrame(self.results)
        df = df[['id', 'original_Results', 'model_response']]
        df.to_excel(output_file, index=False)

async def main():
    # 读取JSON文件并提取Results/Purpose字段
    with open('test_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    Results = [item.get('Results/Findings', '') for item in data]  # 修改字段名

    # 初始化处理器
    processor = ResultsProcessor(api_key="app-0vDNiDJUUz7usGZqLn9L1moo", max_concurrent=10)
    
    # 处理所有背景信息
    await processor.process_all_Results(Results)
    
    # 生成输出文件名
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Results_analysis.xlsx"
    
    # 保存结果
    processor.save_to_excel(output_file)
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
