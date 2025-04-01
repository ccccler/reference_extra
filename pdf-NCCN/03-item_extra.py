import pandas as pd
import aiohttp
import asyncio
import json
import re
from typing import Dict, List
from datetime import datetime

class ReferenceProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.api_key = api_key
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def call_api_sse(self, reference: str, idx: int) -> Dict:
        """使用SSE方式调用API"""
        url = 'http://192.168.1.90:5000/v1/completion-messages'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构造提示词
        prompt = f"""你是一个MAM格式的参考文献信息提取助手,请从以下AMA格式的参考文献中提取以下信息：
        - 文献标题
        - 作者列表
        - 期刊名称
        - 发表年份
        - URL (如果有)
        
        # 请严格按照以下json格式输出，不允许出现任何其他内容：
        {{
            "title": "",
            "authors": "",
            "journal": "",
            "year": "",
            "url": ""
        }}
        
        参考文献：{reference}
        """

        data = {
            "inputs": {"query": prompt},
            "response_mode": "blocking",
            "user": "reference_processor"
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
                        print(f"✓ 完成第 {idx+1} 条参考文献处理")  # 简化为只显示处理完成标记

                        return {
                            "id": idx,
                            "original_reference": reference,
                            "model_response": model_response.strip()
                        }
                    except json.JSONDecodeError as e:
                        raise Exception(f"JSON解析错误: {e}")

        except Exception as e:
            print(f"✗ 第 {idx+1} 条参考文献处理失败: {str(e)}")  # 简化错误输出
            return {
                "id": idx,
                "original_reference": reference,
                "model_response": f"ERROR: {str(e)}"
            }

    async def process_reference(self, reference: str, idx: int) -> Dict:
        """处理单条参考文献"""
        async with self.semaphore:
            await asyncio.sleep(0.5)  # 添加小延迟避免请求过于频繁
            return await self.call_api_sse(reference, idx)

    async def process_all_references(self, references: List[str]):
        """分批处理所有参考文献"""
        batch_size = 50
        results = []
        total_batches = (len(references) + batch_size - 1) // batch_size
        
        print(f"\n开始处理，共 {len(references)} 条参考文献，分 {total_batches} 批处理")
        
        for i in range(0, len(references), batch_size):
            batch = references[i:i + batch_size]
            current_batch = i//batch_size + 1
            print(f"\n处理第 {current_batch}/{total_batches} 批 ({len(batch)} 条)")
            
            tasks = [self.process_reference(ref, idx) for idx, ref in enumerate(batch, start=i)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"✗ 第 {i+j+1} 条记录处理失败")
                    results.append({
                        "id": i+j,
                        "original_reference": references[i+j],
                        "model_response": "ERROR"
                    })
                else:
                    results.append(result)
            
            await asyncio.sleep(2)  # 批次间延迟
        
        self.results = results
        print(f"\n全部处理完成！共处理 {len(references)} 条参考文献")

    def save_to_excel(self, output_file: str):
        """将结果保存到Excel文件"""
        df = pd.DataFrame(self.results)
        # 确保列的顺序
        df = df[['id', 'original_reference', 'model_response']]
        df.to_excel(output_file, index=False)

async def main():
    # 读取输入的Excel文件
    input_file = "./content_lines.xlsx"
    df = pd.read_excel(input_file)
    references = df['Content'].tolist()

    # 初始化处理器
    processor = ReferenceProcessor(api_key="app-0vDNiDJUUz7usGZqLn9L1moo", max_concurrent=100)
    
    # 处理所有参考文献
    await processor.process_all_references(references)
    
    # 生成带时间戳的输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"aioutput.xlsx"
    
    # 保存结果
    processor.save_to_excel(output_file)
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
